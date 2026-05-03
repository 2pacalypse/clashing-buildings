"""
Dependency injection utilities for the API layer.
"""

from fastapi import Request
import redis.asyncio as redis


async def get_redis(request: Request) -> redis.Redis:
    """FastAPI dependency for async Redis client from app.state."""
    return request.app.state.redis
