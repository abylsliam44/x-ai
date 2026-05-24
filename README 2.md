# Agentic X Content Platform

An AI-native editorial system for creating high-signal content for X/Twitter.

> This is not a tweet generator.
> This is an agentic editorial pipeline that researches, drafts, fact-checks, and publishes sharp content.

---

## Product overview

The platform guides a user through a full content lifecycle:

```
Idea / Topic / Link / File / Voice Note
        ↓
Research & Source Grounding
        ↓
Insight Extraction
        ↓
Angle / Thesis Generation
        ↓
Draft Generation
        ↓
Fact-checking + Style Review
        ↓
Human Approval
        ↓
Publish / Schedule / Export
```

**Supported content types:** text posts, threads, quote retweets, image posts, carousel sets, voice-to-post, narrated video posts, research breakdowns.

---

## Architecture

```
Frontend (React + Vite)
        ↕ REST / SSE
Backend (FastAPI + SQLAlchemy)
        ↕
Agent Orchestrator (Research → Angles → Draft → Fact-check → Style → Editor)
        ↕
Celery Workers (Research / Media / Publishing jobs)
        ↕
PostgreSQL · Redis · Object Storage
        ↕
External: OpenAI · X API · Web Search
```

---

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, shadcn/ui |
| Backend | FastAPI, SQLAlchemy 2.x, Alembic, Pydantic v2 |
| Task queue | Celery, Redis |
| Database | PostgreSQL 16 |
| LLM | OpenAI (gpt-5.5 / gpt-5.4-mini with model routing) |
| Image | gpt-image-2 |
| STT | gpt-4o-transcribe / gpt-4o-mini-transcribe |
| TTS | gpt-4o-mini-tts |
| Video | sora-2 |
| Embedding | text-embedding-3-small |
| X publishing | X API v2 (OAuth 2.0 PKCE) |
| Reverse proxy | nginx |

---

## Local development setup

### Prerequisites

- Docker Desktop (or Docker + Docker Compose plugin)
- Node.js 20+ (for frontend dev server)
- Python 3.12+ (for running backend outside Docker)

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd nfactorial
```

### 2. Configure the backend environment

```bash
cp backend/.env.example backend/.env
# Edit backend/.env and fill in your keys:
#   OPENAI_API_KEY=sk-...
#   X_CLIENT_ID=...
#   X_CLIENT_SECRET=...
```

For local development, `MOCK_MODE=true` is the safe default — no real API keys needed.

### 3. Start infrastructure services

```bash
cd backend
docker compose up -d postgres redis
```

### 4. Start the backend

**With Docker (recommended):**
```bash
cd backend
docker compose up -d backend worker beat
```

**Without Docker:**
```bash
cd backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### 5. Start the frontend dev server

```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173
```

The Vite dev server proxies `/api` requests to `http://localhost:8000` automatically.

---

## Environment variables

Key settings in `backend/.env`:

| Variable | Default | Description |
|---|---|---|
| `MOCK_MODE` | `true` | `true` = no real API keys needed |
| `DEFAULT_LLM_PROVIDER` | `mock` | `openai` \| `anthropic` \| `mock` |
| `OPENAI_API_KEY` | — | Required when `MOCK_MODE=false` |
| `OPENAI_MODEL_STRONG` | `gpt-5.5` | Strong-tier model (insight, writer, editor agents) |
| `OPENAI_MODEL_CHEAP` | `gpt-5.4-mini` | Cheap-tier model (research, style, fact-check agents) |
| `ENABLE_REAL_X_API` | `false` | `true` = publish to real X account |
| `X_CLIENT_ID` | — | Required when `ENABLE_REAL_X_API=true` |
| `X_CLIENT_SECRET` | — | Required when `ENABLE_REAL_X_API=true` |

See `backend/.env.example` for the full list.

---

## 13-step demo flow

1. **Register** at `http://localhost:5173` — create an account.
2. **Settings → Brand Voice** — add your writing style, tone, target audience.
3. **Settings → Writing Samples** — paste 2–3 example posts to teach the system your voice.
4. **Settings → Connected Accounts** — click "Connect X Account" and complete OAuth.
5. **Dashboard → New Project** — enter a topic or paste a URL/X post link.
6. **Research workspace** — the Research Agent surfaces key findings, contradictions, and source quality warnings.
7. **Angle selection** — review 5 generated angles; each shows thesis, tone, risk, and format recommendation.
8. **Choose an angle** — click "Use This Angle" to proceed.
9. **Composer Studio** — Writer Agent generates the first draft; Fact Checker and Style Reviewer panels appear on the right.
10. **Review and improve** — use "Improve Hook", "Make Shorter", "Add Specificity", or "Rewrite" actions.
11. **Agent Traces tab** — inspect every agent step: input, output, model, tokens, latency.
12. **Approve Draft** — click "Approve & Publish" only after the quality gate passes.
13. **Published** — the platform posts to X and returns the tweet URL (or schedules it for later).

---

## API endpoints

### Auth
```
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me
```

### X OAuth
```
GET  /api/v1/x/connect
GET  /api/v1/x/callback
GET  /api/v1/x/status
DELETE /api/v1/x/disconnect
```

### Projects
```
POST   /api/v1/projects
GET    /api/v1/projects
GET    /api/v1/projects/{id}
POST   /api/v1/projects/{id}/research
POST   /api/v1/projects/{id}/angles
POST   /api/v1/projects/{id}/drafts/generate
GET    /api/v1/projects/{id}/traces
```

### Drafts
```
GET    /api/v1/drafts/{id}
PATCH  /api/v1/drafts/{id}
POST   /api/v1/drafts/{id}/fact-check
POST   /api/v1/drafts/{id}/revise
POST   /api/v1/drafts/{id}/approve
POST   /api/v1/drafts/{id}/publish/x
```

Full interactive docs at `http://localhost:8000/docs`.

---

## Production deployment

See [deploy/README.md](deploy/README.md) for the full production guide (DigitalOcean Ubuntu, Docker Compose, nginx, Let's Encrypt SSL).

Quick summary:

```bash
# 1. On a fresh Ubuntu 22.04 server:
./deploy/setup_server.sh

# 2. Configure secrets:
cp backend/.env.production.example backend/.env
nano backend/.env   # Fill SECRET_KEY, OPENAI_API_KEY, X_CLIENT_ID, X_CLIENT_SECRET

# 3. Deploy:
./deploy/deploy.sh
```

### X Developer Portal — production redirect URI

In your X Developer app settings, add the **Callback URI**:
```
https://your-domain.com/api/v1/x/callback
```

Set `X_REDIRECT_URI=https://your-domain.com/api/v1/x/callback` in `backend/.env`.

### SSL / HTTPS

```bash
# Install certbot on the server:
apt-get install -y certbot
certbot certonly --webroot -w /var/www/certbot -d your-domain.com

# Then uncomment the HTTPS server block in nginx/conf.d/app.conf
# and reload nginx:
docker compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

---

## Agent model routing

Strong-tier agents (complex reasoning):
- `insight_agent`, `angle_agent`, `draft_writer_agent`, `editor_agent`
→ use `OPENAI_MODEL_STRONG` (default: `gpt-5.5`)

Cheap-tier agents (fast extraction/scoring):
- `research_agent`, `outline_agent`, `style_reviewer_agent`, `fact_checker_agent`, `media_director_agent`
→ use `OPENAI_MODEL_CHEAP` (default: `gpt-5.4-mini`)

Change the routing by editing `backend/app/providers/llm/model_router.py`.

---

## Running tests

```bash
cd backend
docker compose up -d postgres redis
source .venv/bin/activate  # or inside Docker
pytest -v
```

Tests run in `MOCK_MODE=true` automatically — no real API keys needed.

---

## Project structure

```
nfactorial/
├── backend/                  FastAPI backend
│   ├── app/
│   │   ├── agents/           Agent implementations
│   │   ├── api/v1/endpoints/ REST endpoints
│   │   ├── core/             Config, security, DB session
│   │   ├── models/           SQLAlchemy ORM models
│   │   ├── providers/        LLM / search / media providers
│   │   ├── schemas/          Pydantic request/response schemas
│   │   ├── services/         Business logic
│   │   └── workers/          Celery tasks
│   ├── alembic/              Database migrations
│   └── tests/
├── frontend/                 React + Vite frontend
│   └── src/
│       ├── components/       UI components
│       ├── hooks/            TanStack Query hooks
│       ├── lib/              API client, auth utilities
│       └── pages/            Route pages
├── nginx/                    Reverse proxy config
├── deploy/                   Deployment scripts
├── docker-compose.prod.yml   Production Docker Compose
└── CLAUDE.md                 Product and architecture spec
```

---

## Security

- X OAuth tokens are stored AES-256 encrypted; never returned to the frontend raw.
- `backend/.env` is gitignored — never commit secrets.
- Content is never published without explicit user approval in the default mode.
- All agent steps and publish actions are logged in the database.
