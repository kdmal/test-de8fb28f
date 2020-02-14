from flask import current_app
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy(current_app)


class User(db.Model):
    username = db.Column(db.String(100), primary_key=True)
    token = db.Column(db.String(100), unique=True, nullable=False)
    secret = db.Column(db.String(100), nullable=False)
    def __str__(self)->str:
        return f"<User({self.username})>"


class File(db.Model):
    uuid = db.Column(db.String(36), primary_key=True)
    user = db.Column(db.String(100), db.ForeignKey("user.username"),
        nullable=False)
    ext = db.Column(db.Text(), nullable=False, default="")
    salt = db.Column(db.Binary(32), nullable=True)
    nonce = db.Column(db.Binary(), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="NEW")

    @property
    def tmp(self)->str:
        return f"{self.uuid}.tmp"

    @property
    def enc(self)->str:
        return f"{self.uuid}.enc"

    @property
    def name(self)->str:
        return f"{self.uuid}{self.ext}"

    def __str__(self)->str:
        return f"<File({self.uuid}, {self.ext})>"
