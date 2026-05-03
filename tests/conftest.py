"""
Pytest configuration and fixtures for integration testing.

Provides mocked dependencies and test client setup for API tests.
"""

import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient


@pytest.fixture
def client(monkeypatch):
    """
    TestClient with mocked Redis.

    Mocks redis.asyncio.Redis to prevent connecting to actual Redis during
    app startup. Pydantic validation rejects invalid requests before reaching
    the service layer, so no service stubbing is needed.
    """
    # Create a mock Redis instance
    mock_redis_instance = AsyncMock()
    mock_redis_instance.close = AsyncMock()

    # The app awaits redis.Redis(...), so the patched constructor must be awaitable.
    mock_redis_factory = AsyncMock(return_value=mock_redis_instance)

    # Patch redis.asyncio.Redis before importing app
    monkeypatch.setattr("redis.asyncio.Redis", mock_redis_factory)

    # Import and create the app with mocked Redis
    from app.main import app

    with TestClient(app) as client_instance:
        yield client_instance
