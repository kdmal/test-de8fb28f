from flask import current_app as app
from flaskr.celery import create_celery
from flaskr.models import db, User, File
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad
from time import sleep
import os


celery_app = create_celery(app)


@celery_app.task
def encrypt(user, uuid):
    # user
    user = User.query.filter_by(username=user).first()
    if not user: raise Exception("User not found")
    # file
    file = File.query.filter_by(user=user.username, uuid=uuid).first()
    if not file: raise Exception("File not found")
    # encrypt file
    salt = get_random_bytes(32)
    key = PBKDF2(user.secret, salt, dkLen=32)
    cipher = AES.new(key, AES.MODE_EAX)
    with open(
        os.path.join(app.config["UPLOAD_DIR"], file.tmp),
        "rb"
    ) as infile:
        with open(
            os.path.join(app.config["UPLOAD_DIR"], file.enc),
            "wb"
        ) as outfile:
            while True:
                chunk = infile.read(AES.block_size)
                if not chunk: break
                chunk = cipher.encrypt(chunk)
                outfile.write(chunk)
    # delete tmp file
    try:
        os.remove(
            os.path.join(app.config["UPLOAD_DIR"], file.tmp)
        )
    except: pass
    # rename encrypted file
    os.rename(
        os.path.join(app.config["UPLOAD_DIR"], file.enc),
        os.path.join(app.config["UPLOAD_DIR"], file.uuid),
    )
    # save salt
    file.salt = salt
    file.nonce = cipher.nonce
    file.status = "SUCCESS"
    db.session.commit()
    # small delay
    sleep(5)
