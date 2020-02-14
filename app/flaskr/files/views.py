from flask import (
    flash,
    request,
    jsonify,
    stream_with_context,
    Response,
    current_app as app
)
from celery.result import AsyncResult
from uuid import uuid4
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from . import files
from .tasks import encrypt
import os
import hashlib


CHUNK_SIZE = 4096


@files.route("/upload/<uuid>", methods=["DELETE", "GET"])
def upload_by_uuid(uuid):
    from flaskr.models import db, User, File
    try:
        # *** verify token ***
        token = request.headers.get("X-TOKEN")
        user = User.query.filter_by(token=token).first()
        if not user: return jsonify({"error": "Invalid token"}), 401
        # *** delete file ***
        if request.method=="DELETE":
            for file in File.query.filter_by(user=user.username, uuid=uuid):
                # delete from file system
                for fname in (file.uuid, file.tmp, file.enc,):
                    try:
                        os.remove(
                            os.path.join(app.config["UPLOAD_DIR"], fname)
                        )
                    except: pass
                # delete from db
                db.session.delete(file)
            db.session.commit()
        # *** download file ***
        elif request.method=="GET":
            # get uuid from db
            file = File.query.filter_by(user=user.username, uuid=uuid).first()
            if not file: return jsonify({"error": "File not found"}), 404
            # file not exists
            if not os.path.isfile(
                os.path.join(app.config["UPLOAD_DIR"], file.uuid)
            ):
                return jsonify({"error": "File not exists"}), 404
            # return stream
            def stream():
                with open(
                    os.path.join(app.config["UPLOAD_DIR"], file.uuid),
                    "rb"
                ) as f:
                    key = PBKDF2(user.secret, file.salt, dkLen=32)
                    cipher = AES.new(key, AES.MODE_EAX, file.nonce)
                    while True:
                        chunk = f.read(AES.block_size)
                        if chunk: yield cipher.decrypt(chunk)
                        else: break
            return Response(
                stream_with_context(stream()),
                headers={
                    "Content-Disposition": f"attachment; filename={file.name}",
                    "Access-Control-Expose-Headers": "Content-Disposition",
                    "Content-Type": "application/octet-stream",
                }
            )
        # all ok
        return jsonify()
    except Exception as e:
        return jsonify({"error": f"Unexpected error ({type(e)}): {e}"}), 400


@files.route("/upload", methods=["POST", "GET"])
def upload():
    from flaskr.models import db, User, File
    try:
        # *** verify token ***
        token = request.headers.get("X-TOKEN")
        user = User.query.filter_by(token=token).first()
        if not user: return jsonify({"error": "Invalid token"}), 401
        # *** files list ***
        if request.method=="GET":
            return jsonify({"result": [
                dict(
                    uuid=x.uuid,
                    ext=x.ext,
                    status=x.status,
                ) for x in File.query.filter_by(user=user.username)
            ]})
        # *** upload file ***
        elif request.method=="POST":
            # verift filename
            filename = request.headers.get("X-FILENAME")
            if not filename: return jsonify({"error": "Invalid filename"}), 415
            _,ext = os.path.splitext(filename)
            file = File(uuid=str(uuid4()), user=user.username, ext=ext)
            path = os.path.join(app.config["UPLOAD_DIR"], file.tmp)
            # octet stream
            if request.headers.get("Content-Type")=="application/octet-stream":
                with open(file.tmp) as f:
                    f.write(request.data)
            # else try multipart
            if not "file" in request.files:
                return jsonify({"error": "Unsupprted upload method"}), 415
            request.files["file"].save(path)
            # all, return save file and return task job
            db.session.add(file)
            db.session.commit()
            # start encryption
            res = encrypt.apply_async(args=(user.username, file.uuid))
            return jsonify({
                "result": dict(
                    uuid=file.uuid,
                    ext=file.ext,
                    status = res.status,
                    task=res.id
                )
            })
    except Exception as e:
        return jsonify({"error": f"Unexpected error ({type(e)}): {e}"}), 400


@files.route("/status/<task>", methods=["GET"])
def status(task):
    from flaskr import celery_app
    task = AsyncResult(task, app=celery_app)
    return jsonify({"result": task.status})
