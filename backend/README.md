# Agentic X Content Platform — Backend

AI-native multimodal content platform for X/Twitter. The backend is a single FastAPI monolith designed to run on a small Ubuntu box (2 vCPU / 2 GB RAM) and orchestrate research, drafting, fact-checking, style review, media generation, and publishing through agent workflows.

UI and all user-facing text remain English only. Internal code is English as well.

## Verified Backend Run

Verified against Python 3.12 + Postgres 16 + Redis 7 in the Docker image. Every command below has been executed and confirmed to succeed.

### Local run (without Docker)

Requires Python 3.12+ and a reachable Postgres + Redis. The codebase uses PEP 604 syntax (`str | None`), so 3.10 is the absolute minimum.

```bash
cd backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Start Postgres on :5432 and Redis on :6379 first (or use docker compose up -d postgres redis).
alembic upgrade head
uvicorn app.main:app --reload --port 8000
# Browse http://localhost:8000/docs
```

### Docker run (full stack)

```bash
cd backend
cp .env.example .env
docker compose up --build
# This starts postgres, redis, backend, worker, beat.
# Backend at http://localhost:8000, health at /api/v1/health.
```

Expected health response: `{"status":"ok","version":"0.1.0","mock_mode":true}`.

### Migrations

```bash
# Inside the backend service (auto-run on container start):
alembic upgrade head

# Author a new migration:
alembic revision -m "describe change"
```

### Tests

```bash
docker build -t agentic-x-backend:dev .
docker run --rm -v "$PWD":/app -w /app agentic-x-backend:dev pytest
# Expected: 8 passed
```

Tests run against SQLite in-memory and fakeredis, so they need no external services. The test suite covers: health, auth (register/login/me), full draft workflow with traces, thread workflow, image media generation, X mock connect, publish-requires-approval gate, and the full end-to-end mock flow (register → project → writing sample → source → angles → draft → fact-check → approve → connect X → publish → traces).

### Mock workflow example (live API)

With the stack up (`docker compose up`), in another shell:

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"demo@example.com","password":"supersecret1"}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

PID=$(curl -s -X POST http://localhost:8000/api/v1/projects \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"title":"Demo","topic":"Judgment is the new bottleneck in AI engineering"}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['id'])")

curl -s -X POST "http://localhost:8000/api/v1/projects/$PID/generate-draft" \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"type":"text_post"}'
```

### Known limitations

- Real X media upload is a single explicit extension point (`XService._upload_media`); it raises `ProviderError` until you implement the chunked upload flow for your X API tier.
- Real LLM image, audio (TTS), video, and web search providers are stubbed — wire them by replacing the classes in `app/providers/{media,search}/` and toggling the matching `ENABLE_REAL_*` flag.
- pgvector is wired as `float[]` for portability; switch the `rag_chunks.embedding` column to `vector(N)` once the extension is installed.
- The system Python on macOS is often 3.9, which is too old; use Docker or install 3.12.
- Tests use SQLite + fakeredis. Production uses Postgres + Redis; the schema has been verified against Postgres via Alembic.
- No frontend in this repository yet.

## Architecture

```
FastAPI (REST API)
   ├── Auth (JWT)
   ├── Projects / Drafts / Media / Publishing endpoints
   ├── RAG endpoints (writing samples + sources)
   ├── X OAuth + publishing
   └── Agent traces + fact-check reports
        │
        ▼
Agent Workflow (custom orchestrator)
   ResearchAgent → RetrievalAgent → InsightAgent → AngleAgent
   → OutlineAgent → DraftWriterAgent → FactCheckerAgent
   → StyleReviewerAgent → EditorAgent → MediaDirectorAgent → PublisherAgent
        │
        ▼
Service layer (LLM, RAG, Research, Media, FactCheck, Style, Publish, Storage, X)
        │
        ▼
Provider abstractions (LLM, image, audio, video, search, storage)
   - Mock providers ship by default so the whole pipeline runs without paid APIs
        │
        ▼
PostgreSQL + Redis + Celery worker
```

### Key design rules

- AI inference always goes through external APIs — no local models.
- Every agent persists an `agent_traces` row with input, output, model, tokens, latency.
- Every publish goes through `Draft → Review → Approve → Publish`. No auto-publish.
- Providers are interchangeable behind interfaces and feature flags.
- Voice content is published to X as an MP4 video, never as raw audio.

## Tech stack

- FastAPI 0.115, Pydantic v2, SQLAlchemy 2 async, Alembic
- PostgreSQL 16, Redis 7, Celery 5
- httpx for outbound HTTP (X OAuth + Tweets API)
- python-jose, passlib, cryptography for auth and encrypted tokens
- Mock providers for LLM/image/audio/video/search so MVP runs offline

## Local setup

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Start Postgres + Redis (Docker or local)
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

The API is then at `http://localhost:8000`, docs at `/docs`.

## Docker setup

```bash
cd backend
cp .env.example .env
docker compose up --build
```

This starts:
- `postgres` (5432)
- `redis` (6379)
- `backend` (8000) — runs `alembic upgrade head` then gunicorn
- `worker` — Celery worker (concurrency=1)
- `beat` — Celery beat for scheduled publishing

## Mock mode

`MOCK_MODE=true` is the default. With mocks enabled:
- LLM responses come from the deterministic `MockLLMProvider`.
- Image/audio/video generation returns small placeholder bytes.
- Web and X search return curated synthetic results.
- X OAuth and X publishing return mock IDs (no network calls).

Flip the relevant `ENABLE_REAL_*` flag and supply the matching API key/secret to wire a real provider.

## Environment variables

See `.env.example`. The important groups:
- `SECRET_KEY`, `JWT_*` for auth
- `DATABASE_URL`, `REDIS_URL`, `CELERY_*`
- `DEFAULT_LLM_PROVIDER` and provider API keys
- `X_CLIENT_ID`, `X_CLIENT_SECRET`, `X_REDIRECT_URI`
- `MAX_*` size / count limits, kept in config (not hardcoded)
- `ENABLE_PGVECTOR`, `ENABLE_REAL_X_API`, `ENABLE_REAL_MEDIA_GENERATION`, `ENABLE_REAL_WEB_SEARCH`, `MOCK_MODE`

## Migrations

```bash
alembic upgrade head        # apply latest schema
alembic revision -m "name"  # author a new migration
```

## Tests

```bash
cd backend
pytest
```

Tests use SQLite in-memory and run the full app against `MOCK_MODE=true`. Coverage:
- `test_health.py` — health endpoint and mock-mode flag
- `test_auth.py` — register / login / `users/me`
- `test_projects_and_drafts.py` — end-to-end project → angles → draft → fact-check → approve → publish, plus X mock connect flow and verification that publishing requires approval

## RAG

- Writing samples and sources are chunked and stored in `rag_chunks`.
- When `ENABLE_PGVECTOR=false` (default), retrieval uses a BM25-like keyword fallback over the chunk table.
- When `ENABLE_PGVECTOR=true` and an embedding provider is configured, retrieval uses cosine similarity. Schema keeps embeddings as `float[]` so it works without the pgvector extension; swap to the `vector` type once pgvector is installed in your Postgres.

## X integration

The X integration is treated as mandatory. The mock path lets you click through the full OAuth + publish flow without external calls:

1. `GET /api/v1/x/connect` returns an authorization URL (mock URL when mocks are on).
2. `GET /api/v1/x/callback?code=...&state=...` exchanges and stores encrypted tokens.
3. `GET /api/v1/x/status` reports connection state.
4. `DELETE /api/v1/x/disconnect` removes the linkage.
5. Publishing only proceeds when `draft.status == "approved"` (or `scheduled`).

In real mode (`ENABLE_REAL_X_API=true`):
- OAuth 2.0 Authorization Code Flow with PKCE.
- Tokens stored encrypted with Fernet derived from `SECRET_KEY`.
- Text posts use `POST /2/tweets`.
- Threads chain replies via `reply.in_reply_to_tweet_id`.
- Media upload is wired as a clear extension point (`XService._upload_media`) because the X media chunked upload flow varies by tier — left as a single integration point to fill in for your account.

## Agent traces

Every agent step writes a row in `agent_traces` with input, output, model, latency, status, and token counts. Query them via:
- `GET /api/v1/projects/{project_id}/traces`
- `GET /api/v1/traces/draft/{draft_id}`

Example trace dumps for `text_post`, `thread`, and `voice_video_post` workflows live in [`agent_traces_examples/`](./agent_traces_examples). These mirror the structure produced by the live workflow.

## Endpoints (selected)

```
GET    /api/v1/health
POST   /api/v1/auth/register
POST   /api/v1/auth/login
GET    /api/v1/users/me

GET    /api/v1/x/connect
GET    /api/v1/x/callback
GET    /api/v1/x/status
DELETE /api/v1/x/disconnect

POST   /api/v1/projects
GET    /api/v1/projects
GET    /api/v1/projects/{id}
PATCH  /api/v1/projects/{id}
POST   /api/v1/projects/{id}/generate-angles
POST   /api/v1/projects/{id}/generate-draft
GET    /api/v1/projects/{id}/traces

GET    /api/v1/drafts/{id}
POST   /api/v1/drafts/{id}/revise
POST   /api/v1/drafts/{id}/fact-check
POST   /api/v1/drafts/{id}/approve
POST   /api/v1/drafts/{id}/publish
POST   /api/v1/drafts/{id}/schedule-publish

POST   /api/v1/rag/writing-samples
GET    /api/v1/rag/writing-samples
POST   /api/v1/rag/sources
GET    /api/v1/rag/sources
POST   /api/v1/rag/search
GET    /api/v1/rag/search?q=...

POST   /api/v1/media/generate-image
POST   /api/v1/media/generate-carousel
POST   /api/v1/media/generate-voice-video
POST   /api/v1/media/generate-video
GET    /api/v1/media/{id}

GET    /api/v1/fact-check/draft/{id}
GET    /api/v1/publish/jobs
GET    /api/v1/publish/jobs/{id}
GET    /api/v1/traces/draft/{id}
```

## 2 vCPU / 2 GB RAM deployment notes

- Run the API with one gunicorn worker (`--workers 1`) using `uvicorn.workers.UvicornWorker`.
- Run Celery with `--concurrency=1` and `--prefetch-multiplier=1`.
- Add at least 1 GB swap. Long media generation is bursty.
- Keep media externally hosted in production (`STORAGE_PROVIDER=s3`).
- Disable pgvector unless you actually need vector search; the BM25 fallback is sufficient for MVP.

## Known limitations

- Real X media upload is left as a single extension point — chunked upload flows differ by tier and require account-specific testing.
- The real OpenAI / Anthropic / Tavily / Stability / Runway providers are stubbed; their `*Provider` classes raise a clear `ProviderError` until you implement them.
- pgvector is wired as `float[]` for simplicity; switch to the `vector` type once your DB has the extension.
- No frontend in this repository yet — backend only.

## Next prompt (frontend)

Build the React + TypeScript + Tailwind + shadcn/ui frontend that talks to this backend, with screens for: Login, Dashboard, Project Wizard, Research Workspace, Angle Selection, Composer Studio, Media Studio, Review & Publish, Agent Traces, Settings. UI must be English only. Show the agent workflow visibly — research, insights, angles, draft, fact-check, style — so the product feels agentic, not like an AI wrapper.
