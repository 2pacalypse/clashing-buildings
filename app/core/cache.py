import json
import redis.asyncio as redis
from typing import List, Optional
from app.core.config import settings
from app.models.canonical import CanonicalBuildingIntersection, CanonicalBuilding, CanonicalPolygon
from shapely.geometry import Polygon

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


def _reconstruct_intersection(data: dict) -> CanonicalBuildingIntersection:
    """Reconstruct CanonicalBuildingIntersection from dict, converting coordinate lists back to Polygons."""
    polygon = Polygon(data["intersection"]["base"]["polygon"])
    canonical_polygon = CanonicalPolygon(polygon=polygon)
    canonical_building = CanonicalBuilding(
        elevation=data["intersection"]["elevation"],
        height=data["intersection"]["height"],
        base=canonical_polygon
    )
    return CanonicalBuildingIntersection(
        building_ids=tuple(data["building_ids"]),
        intersection=canonical_building
    )


async def get_cache(key: str) -> Optional[List[CanonicalBuildingIntersection]]:
    """Get cached result by key."""
    client = await get_redis()
    data = await client.get(key)
    if data:
        cached_data = json.loads(data)
        return [_reconstruct_intersection(item) for item in cached_data]
    return None

async def set_cache(key: str, value: List[CanonicalBuildingIntersection], ttl: int = None) -> bool:
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

async def set_job_status(job_id: str, status: str, ttl: int = None) -> None:
    client = await get_redis()
    ttl = ttl or settings.CACHE_TTL
    await client.setex(f"job:{job_id}:status", ttl, status)

async def get_job_status(job_id: str) -> Optional[str]:
    client = await get_redis()
    return await client.get(f"job:{job_id}:status")

async def set_original_ids(job_id: str, original_ids: list, ttl: int = None) -> None:
    client = await get_redis()
    ttl = ttl or settings.CACHE_TTL
    await client.setex(f"job:{job_id}:mapping", ttl, json.dumps(original_ids))

async def get_original_ids(job_id: str) -> Optional[list]:
    client = await get_redis()
    val = await client.get(f"job:{job_id}:mapping")
    return json.loads(val) if val else None