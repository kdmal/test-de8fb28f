from os import getenv

UPLOAD_DIR = getenv("UPLOAD_DIR", "/mnt/files")

CELERY_RESULT_BACKEND = getenv("CELERY_RESULT_BACKEND",
    "redis://localhost:6379")
CELERY_BROKER_URL = getenv("CELERY_BROKER_URL",
    "redis://localhost:6379")

SQLALCHEMY_DATABASE_URI = getenv("DATABASE", "sqlite:////mnt/data/sqlite3.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False

TEMPLATES_AUTO_RELOAD = True

