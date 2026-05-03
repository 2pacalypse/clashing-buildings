from typing import Optional
from fastapi import Request
import redis.asyncio as redis
import redis as redis_sync
from app.core.config import settings


# Synchronous Redis client for use in Celery workers (lazy singleton)
_sync_redis_client: Optional[redis_sync.Redis] = None


def get_sync_redis() -> redis_sync.Redis:
    """Get or create sync Redis client for Celery workers."""
    global _sync_redis_client
    if _sync_redis_client is None:
        _sync_redis_client = redis_sync.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
        )
    return _sync_redis_client


async def get_redis(request: Request) -> redis.Redis:
    """FastAPI dependency for async Redis client from app.state."""
    return request.app.state.redis
