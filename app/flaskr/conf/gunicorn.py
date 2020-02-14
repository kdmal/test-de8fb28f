from multiprocessing import cpu_count
import os


workers = int(
    os.getenv("GUNICORN_WORKERS", cpu_count())
)

bind = "{host}:{port}".format(
    host=os.getenv("GUNICORN_HOST", "0.0.0.0"),
    port=int(os.getenv("GUNICORN_PORT", "8080"))
)

reload = os.getenv("DEV", "").lower() in ("on", "true")

accesslog = os.getenv("GUNICORN_ACCESSLOG", "-")
errorlog = os.getenv("GUNICORN_ERRORLOG", "-")
loglevel = os.getenv("GUNICORN_LOGLEVEL", "INFO")

worker_tmp_dir = os.getenv("GUNICORN_TEMPDIR", "/mnt/tmp")
