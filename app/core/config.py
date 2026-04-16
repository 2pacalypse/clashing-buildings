import os
from functools import lru_cache

class Settings:
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
