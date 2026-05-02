"""Request tracking and mapping caching layer."""

import json
from typing import Optional, List
from app.core.cache import get_redis
from app.core.config import settings


async def get_request_job_id(request_id: str) -> Optional[str]:
    """Get the job_id mapped to a request_id from cache."""
    client = await get_redis()
    val = await client.get(f"requestId:{request_id}:jobId")
    return val if val else None


async def set_request_job_id(request_id: str, job_id: str, ttl: int = None) -> None:
    """Set the job_id for a request_id in cache."""
    client = await get_redis()
    ttl = ttl or settings.CACHE_TTL
    await client.setex(f"requestId:{request_id}:jobId", ttl, job_id)


async def set_request_building_names(
    request_id: str, building_names: list, ttl: int = None
) -> None:
    """Store the building names for a request_id in cache."""
    client = await get_redis()
    ttl = ttl or settings.CACHE_TTL
    await client.setex(
        f"requestId:{request_id}:buildingNames", ttl, json.dumps(building_names)
    )


async def get_request_building_names(request_id: str) -> Optional[List[str]]:
    """Retrieve the building names for a request_id from cache."""
    client = await get_redis()
    val = await client.get(f"requestId:{request_id}:buildingNames")
    return json.loads(val) if val else None
