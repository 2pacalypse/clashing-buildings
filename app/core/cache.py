from typing import Optional
import redis.asyncio as redis
import redis as redis_sync
from app.core.config import settings



redis_client: Optional[redis.Redis] = None

# Synchronous Redis client for use in Celery workers
_sync_redis_client: Optional[redis_sync.Redis] = None


def get_sync_redis() -> redis_sync.Redis:
    global _sync_redis_client
    if _sync_redis_client is None:
        _sync_redis_client = redis_sync.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
        )
    return _sync_redis_client


async def get_redis() -> redis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
        )
    return redis_client
