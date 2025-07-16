from celery import Celery
from app.core.config import settings

celery = Celery(
    "app",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

# Import tasks so they are registered with Celery
celery.autodiscover_tasks(['app.tasks']) 