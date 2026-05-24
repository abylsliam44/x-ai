from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "agentic_x",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_concurrency=settings.CELERY_WORKER_CONCURRENCY,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_default_queue="default",
    broker_connection_retry_on_startup=True,
)

celery_app.conf.beat_schedule = {
    "process-scheduled-publishes": {
        "task": "app.workers.tasks.process_scheduled_publishes",
        "schedule": crontab(minute="*"),
    },
}
