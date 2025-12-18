import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
backend_url = os.getenv("CELERY_RESULT_BACKEND", broker_url)

celery_app = Celery(
    "recipe_pipeline",
    broker=broker_url,
    backend=backend_url,
    include=["tasks"],
)

celery_app.conf.update(
    task_track_started=True,
    result_extended=True,
    result_expires=60 * 60 * 24,  # 24h
    timezone="Asia/Seoul",
    enable_utc=True,
)
