from celery import Celery
import json
import redis
from app.algorithms.clash_detector import detect_clashes
from app.core.cache import set_cache
from app.core.config import settings
from app.models.canonical import CanonicalBuildingSet

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
def detect_clashes_task(buildings_dump: dict, job_id: str):
    """Async task for clash detection."""

    # Reconstruct canonical model and compute collisions
    building_set = CanonicalBuildingSet.model_validate(buildings_dump)
    collisions = detect_clashes(building_set)
    
    # Serialize collisions the same way set_cache does
    serialized = [c.model_dump() for c in collisions]

    # Serialize collisions the same way set_cache does
    # Use a sync Redis client inside Celery worker to avoid asyncio issues
    sync_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB, decode_responses=True)
    sync_client.setex(job_id, settings.CACHE_TTL, json.dumps(serialized))

    sync_client.delete(f"job:{job_id}:status")
    return {"job_id": job_id, "status": "completed"}
