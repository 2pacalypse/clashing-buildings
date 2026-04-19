import json
import redis.asyncio as redis
import redis as redis_sync
from typing import Any, Optional
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
            decode_responses=True
        )
    return _sync_redis_client

async def get_redis() -> redis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )
    return redis_client


async def get_cache(key: str) -> Optional[Any]:
    """Get cached result by key as raw data."""
    client = await get_redis()
    data = await client.get(key)
    return json.loads(data) if data else None

async def set_cache(key: str, value: Any, ttl: int = None) -> bool:
    """Set cache with optional TTL."""
    client = await get_redis()
    ttl = ttl or settings.CACHE_TTL
    serialized = [v.model_dump() for v in value]
    await client.setex(key, ttl, json.dumps(serialized))
    return True



async def claim_job(job_id: str, ttl: int = None) -> bool:
    client = await get_redis()
    ttl = ttl or settings.CACHE_TTL
    # returns True if key was set (we claimed it), None/False otherwise
    return await client.set(f"job:{job_id}:status", "processing", nx=True, ex=ttl)

async def set_original_ids(job_id: str, original_ids: list, ttl: int = None) -> None:
    client = await get_redis()
    ttl = ttl or settings.CACHE_TTL
    await client.setex(f"job:{job_id}:mapping", ttl, json.dumps(original_ids))

async def get_original_ids(job_id: str) -> Optional[list]:
    client = await get_redis()
    val = await client.get(f"job:{job_id}:mapping")
    return json.loads(val) if val else None