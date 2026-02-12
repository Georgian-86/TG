import os
from celery import Celery
from app.config import settings

# Redis URL from config
REDIS_URL = settings.REDIS_URL

celery_app = Celery(
    "teachgenie_worker",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Improve reliability
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
)
