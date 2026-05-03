"""Task ID deduplication layer for input-based caching."""

from typing import Optional
import redis.asyncio as redis
from app.core.config import settings


async def get_task_id(client: redis.Redis, job_id: str) -> Optional[str]:
    """Get the Celery task_id for a job_id. Returns None if no task exists."""
    return await client.get(f"job:{job_id}:task_id")


async def try_claim_job(client: redis.Redis, job_id: str, ttl: int = None) -> bool:
    """Atomically claim a job for processing. Returns True if claimed, False if already claimed."""
    ttl = ttl or settings.CACHE_TTL
    # Try to set a placeholder - only succeeds if key doesn't exist
    return await client.set(f"job:{job_id}:task_id", "processing", nx=True, ex=ttl)


async def store_task_id(client: redis.Redis, job_id: str, task_id: str, ttl: int = None) -> None:
    """Store the actual task_id after claiming (overwrites the placeholder)."""
    ttl = ttl or settings.CACHE_TTL
    await client.setex(f"job:{job_id}:task_id", ttl, task_id)
