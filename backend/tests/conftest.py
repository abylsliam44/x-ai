import asyncio
import os
import sys
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ.setdefault("MOCK_MODE", "true")
os.environ.setdefault("DEFAULT_LLM_PROVIDER", "mock")
os.environ.setdefault("ENABLE_PGVECTOR", "false")
os.environ.setdefault("STORAGE_PROVIDER", "local")
os.environ.setdefault("LOCAL_STORAGE_PATH", str(ROOT / "tests" / ".storage"))
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["DATABASE_SYNC_URL"] = "sqlite:///:memory:"

from app.core.config import get_settings  # noqa: E402
get_settings.cache_clear()  # type: ignore[attr-defined]

import fakeredis.aioredis  # noqa: E402

from app.core import redis as redis_module  # noqa: E402

_fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
redis_module._redis_client = _fake_redis
redis_module.get_redis = lambda: _fake_redis  # type: ignore[assignment]

from app.core.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402

import app.services.x_service as _x_service_module  # noqa: E402

_x_service_module.get_redis = lambda: _fake_redis  # type: ignore[assignment]


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def _prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture()
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
