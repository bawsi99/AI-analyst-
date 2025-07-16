from celery import Celery
from app.core.config import settings
import os
import sys

# Add the app directory to Python path
app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

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
try:
    celery.autodiscover_tasks(['app.tasks'])
except Exception as e:
    print(f"Error discovering tasks: {e}")
    import traceback
    traceback.print_exc() 