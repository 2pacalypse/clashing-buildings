from fastapi import Request
import redis.asyncio as redis

#todo: move this to main.py?
async def get_redis(request: Request) -> redis.Redis:
    """FastAPI dependency for async Redis client from app.state."""
    return request.app.state.redis
