from celery import Celery
from app.core.config import settings
from app.algorithms.clash_detector import detect_clashes
from app.core.cache import set_cache

celery_app = Celery(
    'clash_detector',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@celery_app.task(name='detect_clashes_task')
def detect_clashes_task(buildings: list, content_hash: str):
    """Async task for clash detection."""
    result = detect_clashes(buildings)
    
    # Cache the result
    set_cache(content_hash, result)
    
    return result
