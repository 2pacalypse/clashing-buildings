"""Clash detection caching layer with domain-specific logic and key patterns."""
import json
from typing import List, Optional
from app.core.cache import get_redis
from app.core.config import settings
from app.models.canonical import CanonicalBuildingIntersection


async def get_clash_results(job_id: str) -> Optional[List[CanonicalBuildingIntersection]]:
    """Get cached clash results and deserialize to models."""
    client = await get_redis()
    data = await client.get(job_id)
    if data:
        cached_data = json.loads(data)
        return [CanonicalBuildingIntersection.model_validate(item) for item in cached_data]
    return None


async def set_clash_results(job_id: str, collisions: List[CanonicalBuildingIntersection], ttl: int = None) -> bool:
    """Serialize and cache clash results."""
    client = await get_redis()
    ttl = ttl or settings.CACHE_TTL
    serialized = [c.model_dump() for c in collisions]
    await client.setex(job_id, ttl, json.dumps(serialized))
    return True


async def claim_job(job_id: str, ttl: int = None) -> bool:
    """Try to claim a job for processing. Returns True if claimed, False if already claimed."""
    client = await get_redis()
    ttl = ttl or settings.CACHE_TTL
    return await client.set(f"job:{job_id}:status", "processing", nx=True, ex=ttl)


async def set_original_ids(job_id: str, original_ids: list, ttl: int = None) -> None:
    """Store the mapping of canonical building indices to original feature IDs."""
    client = await get_redis()
    ttl = ttl or settings.CACHE_TTL
    await client.setex(f"job:{job_id}:mapping", ttl, json.dumps(original_ids))


async def get_original_ids(job_id: str) -> Optional[list]:
    """Retrieve the original feature ID mapping for a job."""
    client = await get_redis()
    val = await client.get(f"job:{job_id}:mapping")
    return json.loads(val) if val else None
