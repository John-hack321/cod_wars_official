from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.worker"],  # Add the path to your tasks module here
)

celery_app.conf.update(
    task_track_started=True,
)
