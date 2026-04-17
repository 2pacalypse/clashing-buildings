import json
import hashlib
import redis.asyncio as redis
from typing import Optional, Any
from app.core.config import settings

redis_client: Optional[redis.Redis] = None

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


async def get_cache(key: str) -> Optional[dict]:
    """Get cached result by key."""
    client = await get_redis()
    data = await client.get(f"clash:{key}")
    if data:
        return json.loads(data)
    return None

async def set_cache(key: str, value: dict, ttl: int = None) -> bool:
    """Set cache with optional TTL."""
    client = await get_redis()
    ttl = ttl or settings.CACHE_TTL
    await client.setex(f"clash:{key}", ttl, json.dumps(value))
    return True
