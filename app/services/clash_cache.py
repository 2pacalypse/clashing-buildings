"""Clash detection caching layer with domain-specific logic and key patterns."""

import json
from typing import List, Optional
import redis.asyncio as redis
from app.core.config import settings
from app.models.canonical import CanonicalBuildingIntersection


async def get_clash_results(
    client: redis.Redis,
    job_id: str,
) -> Optional[List[CanonicalBuildingIntersection]]:
    """Get cached clash results and deserialize to models."""
    data = await client.get(job_id)
    if data:
        cached_data = json.loads(data)
        return [
            CanonicalBuildingIntersection.model_validate(item) for item in cached_data
        ]
    return None


async def set_clash_results(
    client: redis.Redis,
    job_id: str,
    collisions: List[CanonicalBuildingIntersection],
    ttl: int = None,
) -> None:
    """Serialize and cache clash results."""
    ttl = ttl or settings.CACHE_TTL
    serialized = [c.model_dump() for c in collisions]
    await client.setex(job_id, ttl, json.dumps(serialized))


def set_clash_results_sync(
    job_id: str, collisions: List[CanonicalBuildingIntersection], ttl: int = None
) -> None:
    """Sync version: Serialize and cache clash results."""
    client = get_sync_redis()
    ttl = ttl or settings.CACHE_TTL
    serialized = [c.model_dump() for c in collisions]
    client.setex(job_id, ttl, json.dumps(serialized))


async def claim_job(client: redis.Redis, job_id: str, ttl: int = None) -> bool:
    """Try to claim a job for processing. Returns True if claimed, False if already claimed."""
    ttl = ttl or settings.CACHE_TTL
    return await client.set(f"job:{job_id}:status", "processing", nx=True, ex=ttl)


async def job_exists(client: redis.Redis, job_id: str) -> bool:
    """Check if a job has been claimed (submitted for processing)."""
    status = await client.get(f"job:{job_id}:status")
    return status is not None
