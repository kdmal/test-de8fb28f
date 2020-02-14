from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from .celery import create_celery


def create_app():
    app = Flask(__name__)
    app.config.from_object("flaskr.conf.settings")
    with app.app_context():
        from .files import files
        app.register_blueprint(files, url_prefix="/files")
    return app


app = create_app()
celery_app = create_celery(app)


@app.route("/", methods=["GET"])
def default():
    return render_template("index.html")


@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"result": "pong"})


@app.route("/tokens", methods=["GET"])
def tokens():
    from .models import User
    return jsonify({
        "result": [ x.token for x in User.query.with_entities(User.token) ]
    })
