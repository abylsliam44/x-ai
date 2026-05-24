"""
Integration test conftest — uses REAL providers (OpenAI, etc.).

Key differences from tests/conftest.py (mock suite):
  - MOCK_MODE stays false → real LLM, real image, real STT/TTS, real web search
  - Uses a SEPARATE database: agentic_x_test  (created by run_integration_tests.sh)
  - ENABLE_REAL_X_API is forced to false → X publishing stays safe
  - ENABLE_REAL_VIDEO_GENERATION forced to false (disabled in prod anyway)

Run:
    cd /app && python -m pytest integration_tests/ -v -s
or via script (recommended):
    ./backend/scripts/run_integration_tests.sh
"""
import asyncio
import os
import sys
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# ── 1. Override DATABASE_URL to test DB BEFORE any app import ─────────────────
# The test DB (agentic_x_test) is created by run_integration_tests.sh before
# pytest runs. conftest just points the engine at it.

_raw_db_url = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@postgres:5432/agentic_x",
)
_raw_sync_url = os.environ.get(
    "DATABASE_SYNC_URL",
    "postgresql+psycopg://postgres:postgres@postgres:5432/agentic_x",
)
TEST_DB = "agentic_x_test"
os.environ["DATABASE_URL"] = _raw_db_url.rsplit("/", 1)[0] + "/" + TEST_DB
os.environ["DATABASE_SYNC_URL"] = _raw_sync_url.rsplit("/", 1)[0] + "/" + TEST_DB

# ── 2. Safety overrides ───────────────────────────────────────────────────────
os.environ["MOCK_MODE"] = "false"
os.environ["ENABLE_REAL_X_API"] = "false"            # never post to real X
os.environ["ENABLE_REAL_VIDEO_GENERATION"] = "false" # disabled in prod anyway
os.environ.setdefault("STORAGE_PROVIDER", "local")

# ── 3. Clear cached settings / providers ─────────────────────────────────────
from app.core.config import get_settings          # noqa: E402
from app.providers.llm.factory import get_llm_provider  # noqa: E402

get_settings.cache_clear()
get_llm_provider.cache_clear()

# ── 4. Wire in fakeredis (same trick as mock conftest) ────────────────────────
import fakeredis.aioredis                         # noqa: E402
from app.core import redis as _redis_module       # noqa: E402

_fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
_redis_module._redis_client = _fake_redis
_redis_module.get_redis = lambda: _fake_redis     # type: ignore[assignment]

import app.services.x_service as _x_svc          # noqa: E402

_x_svc.get_redis = lambda: _fake_redis            # type: ignore[assignment]

# ── 5. Import app AFTER env overrides ─────────────────────────────────────────
from app.core.database import Base, engine        # noqa: E402
from app.main import app                          # noqa: E402


# ── 6. Session-scoped event loop (mirrors mock conftest) ──────────────────────

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ── 7. Per-test DB reset (same pattern as mock conftest) ─────────────────────
# Tables were created by run_integration_tests.sh via `alembic upgrade head`.
# We just truncate between tests for isolation.

@pytest_asyncio.fixture(autouse=True)
async def _reset_tables():
    """Drop and recreate schema before each test for clean isolation."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ── 8. HTTP client fixture ────────────────────────────────────────────────────

@pytest_asyncio.fixture()
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


# ── 9. Ready-made auth headers ────────────────────────────────────────────────

@pytest_asyncio.fixture()
async def auth_headers(client):
    """Register a fresh test user and return Bearer headers."""
    import uuid

    email = f"int-{uuid.uuid4().hex[:8]}@example.com"
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "IntegrationTest1!"},
    )
    assert r.status_code == 201, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}
