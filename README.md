<div align="center">

# Agentic X Content Platform

**An AI-native editorial system for researching, drafting, fact-checking, and publishing high-signal content on X/Twitter.**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=111827)](https://react.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://postgresql.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--5.5-412991?style=flat-square&logo=openai&logoColor=white)](https://openai.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docs.docker.com/compose)
[![DigitalOcean](https://img.shields.io/badge/DigitalOcean-Deployed-0080FF?style=flat-square&logo=digitalocean&logoColor=white)](https://digitalocean.com)

<br/>

> **This is not a tweet generator.**
> This is an agentic editorial pipeline where every step — research, insight extraction, angle generation, drafting, fact-checking, style review — is performed by a specialized AI agent, and humans approve every gate before publishing.

</div>

---

## Table of Contents

- [Why This Exists](#why-this-exists)
- [Architecture Overview](#architecture-overview)
- [Agent Pipeline](#agent-pipeline)
  - [Agent Roster](#agent-roster)
  - [Workflow Execution Graph](#workflow-execution-graph)
  - [Model Routing](#model-routing)
- [Tech Stack](#tech-stack)
- [Content Types](#content-types)
- [Data Model](#data-model)
- [API Reference](#api-reference)
- [Local Development](#local-development)
- [Production Deployment](#production-deployment)
- [Environment Variables](#environment-variables)
- [Security](#security)
- [Project Structure](#project-structure)

---

## Why This Exists

Most AI writing tools produce the same output: confident, generic, forgettable. They generate text without grounding it in evidence, without checking if claims are true, and without adapting to the author's actual voice.

This platform is built around a different assumption: good content requires a workflow, not a button.

```
Idea / Topic / URL / File / Voice Note
              │
              ▼
    ┌─────────────────┐
    │  Research Agent │  ← Web search + RAG over writing samples
    └────────┬────────┘
             │ sources, key findings, contradictions
             ▼
    ┌─────────────────┐
    │  Insight Agent  │  ← Extracts non-obvious, defensible claims
    └────────┬────────┘
             │ ranked insights with evidence refs
             ▼
    ┌─────────────────┐
    │   Angle Agent   │  ← 5 contrarian-but-defensible angles
    └────────┬────────┘
             │ human selects one angle
             ▼
    ┌──────────────────┐
    │  Outline Agent   │  ← Structures beats by content type
    └────────┬─────────┘
             │ section / beat outline
             ▼
    ┌──────────────────────┐
    │  Draft Writer Agent  │  ← Writes to voice, no AI clichés
    └────────┬─────────────┘
             │ raw draft
             ▼
    ┌────────────────────────┐   ┌───────────────────────┐
    │  Fact Checker Agent    │   │  Style Reviewer Agent  │
    │  claim → verdict table │   │  voice match score     │
    └────────┬───────────────┘   └──────────┬────────────┘
             └──────────┬──────────────────┘
                        │ reports injected
                        ▼
             ┌──────────────────┐
             │   Editor Agent   │  ← Hook, rhythm, density, cuts
             └────────┬─────────┘
                      │ revised draft + change log
                      ▼
             ┌────────────────────────┐
             │  Media Director Agent  │  ← Visual brief (optional)
             └────────┬───────────────┘
                      │ human approves
                      ▼
             ┌────────────────────┐
             │  Publisher Agent   │  ← Only runs on approved drafts
             └────────────────────┘
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Browser Client                          │
│              React 18 · TypeScript · Tailwind CSS               │
│         TanStack Query · React Router · IBM Plex Mono           │
└──────────────────────────────┬──────────────────────────────────┘
                                │  REST + SSE
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     nginx  (reverse proxy)                      │
│               SSL termination · static file serving             │
└──────────────────────────────┬──────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                 FastAPI Backend  (Gunicorn / Uvicorn)            │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────────────┐   │
│  │  Auth / JWT  │  │  Projects   │  │  Drafts / Approvals  │   │
│  └──────────────┘  └─────────────┘  └──────────────────────┘   │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────────────┐   │
│  │  X OAuth 2.0 │  │    Media    │  │  Agent Traces / RAG  │   │
│  └──────────────┘  └─────────────┘  └──────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────┘
                                │
              ┌─────────────────┼──────────────────┐
              │                 │                  │
              ▼                 ▼                  ▼
┌─────────────────┐  ┌───────────────────┐  ┌──────────────────┐
│ ContentWorkflow │  │   Celery Worker   │  │   Celery Beat    │
│ (in-request)    │  │   (async jobs)    │  │   (scheduler)    │
│                 │  │                   │  │                  │
│ ResearchAgent   │  │  research_jobs    │  │  scheduled posts │
│ RetrievalAgent  │  │  media_jobs       │  │                  │
│ InsightAgent    │  │  publish_jobs     │  │                  │
│ AngleAgent      │  │                   │  │                  │
│ OutlineAgent    │  └───────────────────┘  └──────────────────┘
│ DraftWriter     │
│ FactChecker     │
│ StyleReviewer   │
│ EditorAgent     │
│ MediaDirector   │
│ PublisherAgent  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                          Storage Layer                          │
│  ┌───────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │  PostgreSQL   │  │    Redis     │  │    Object Storage    │ │
│  │  primary DB   │  │  broker /    │  │  media assets        │ │
│  │  pgvector opt │  │  cache       │  │  local or S3         │ │
│  └───────────────┘  └──────────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                       External Providers                        │
│   OpenAI (LLM · Image · STT · TTS)  ·  X API v2  ·  Search     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Agent Pipeline

### Agent Roster

Each agent is a `BaseAgent` subclass with a single `async def run(context, payload) → AgentResult` method. All inputs, outputs, model choices, token usage, and latency are persisted to `agent_traces`.

---

#### `ResearchAgent`
`backend/app/agents/research_agent.py`

Calls the configured search provider (OpenAI web search or mock) with the project topic. Returns ranked results with title, URL, snippet, published date, and credibility score.

```
Input  → { topic: str }
Output → { results: [{ title, url, snippet, published_at, score }] }
Model  → cheap-tier
```

---

#### `RetrievalAgent`
`backend/app/agents/retrieval_agent.py`

Performs vector search over the user's uploaded writing samples. Returns the top-K semantically similar chunks that inform style context for the writer and editor.

```
Input  → { topic: str }
Output → { chunks: [{ text, score, source_id }] }
Model  → text-embedding-3-small
```

---

#### `InsightAgent`
`backend/app/agents/insight_agent.py`

Takes research results and RAG chunks. Extracts non-obvious, defensible claims with evidence references. Explicitly penalises generic statements like "AI is changing everything."

```
Input  → { topic, research[], rag_chunks[] }
Output → { insights: [{ insight, why_it_matters, evidence_refs[] }] }
Model  → strong-tier (gpt-5.5)
```

---

#### `AngleAgent`
`backend/app/agents/angle_agent.py`

Produces 5 sharp, contrarian-but-defensible angles. Each angle includes a title, thesis, hook (first line of the post), and rationale. Considers the user's goal and target audience.

```
Input  → { topic, goal, target_audience, insights[], count }
Output → { angles: [{ title, thesis, hook, rationale }] }
Model  → strong-tier (gpt-5.5)
```

---

#### `OutlineAgent`
`backend/app/agents/outline_agent.py`

Structures the selected angle into a content-type-specific outline. Threads get 3–6 sections; text posts get 2–3; research articles get 4–7.

```
Input  → { type, angle, rag_chunks[] }
Output → { outline: [{ section, beats[] }] }
Model  → cheap-tier (gpt-5.4-mini)
```

---

#### `DraftWriterAgent`
`backend/app/agents/draft_writer_agent.py`

Writes the first draft using the outline, style context from writing samples, and the angle thesis. Hard constraints: no emojis, no hashtags by default, no filler phrases, concrete claims only.

| `type` | Output shape |
|--------|-------------|
| `text_post` | `{ text: str }` |
| `thread` | `{ thread_items: [{ index, text }] }` |
| `quote_retweet` | `{ text: str, quote_url: str }` |
| `research_article` | `{ title: str, text: str }` |

```
Model → strong-tier (gpt-5.5)
```

---

#### `FactCheckerAgent`
`backend/app/agents/fact_checker_agent.py`

Extracts all factual claims from the draft, fetches supporting evidence from the search provider and RAG, then returns a verdict per claim. Persists each claim to the `fact_checks` table.

```
Verdicts → supported | weakly_supported | contradicted | unverifiable

Input  → { draft_id }
Output → { claims: [{ claim, verdict, confidence, evidence[], suggested_fix }],
           overall_score: float }
Model  → cheap-tier (gpt-5.4-mini)
```

---

#### `StyleReviewerAgent`
`backend/app/agents/style_reviewer_agent.py`

Compares the draft against the user's writing samples. Returns a 0–10 score, voice matches, mismatches, and suggested adjustments.

```
Input  → { draft_id, style_context }
Output → { score: float, matches[], mismatches[], adjustments[] }
Model  → cheap-tier (gpt-5.4-mini)
```

---

#### `EditorAgent`
`backend/app/agents/editor_agent.py`

Receives the draft plus both review reports. Improves hook strength, cuts filler, sharpens rhythm, removes overclaiming. Also applies free-text user instructions ("make it shorter", "remove the last paragraph"). Writes revised content directly back to the `Draft` record.

```
Input  → { draft_id, fact_check, style, instructions }
Output → { revised_text | revised_thread_items, changes_made[] }
Model  → strong-tier (gpt-5.5)
```

---

#### `MediaDirectorAgent`
`backend/app/agents/media_director_agent.py`

Only runs when `include_media=true`. Creates a visual brief for each planned asset. The workflow then materialises each item via `MediaService`.

```
Input  → { type, angle, text, media_preferences }
Output → { media_plan: [{ type, prompt, aspect_ratio, notes }] }
Model  → cheap-tier (gpt-5.4-mini)
```

---

#### `PublisherAgent`
`backend/app/agents/publisher_agent.py`

**Never runs unless `draft.status == "approved"`**. Creates a `PublishJob`, calls `XService.publish_draft()`, and handles the full X API flow: text posts, thread reply chains, chunked video upload, and media attachment.

```
Input  → { draft_id, scheduled_at? }
Output → { job_id, platform_post_id, status }
```

---

### Workflow Execution Graph

```
generate_angles()                      generate_draft()
        │                                      │
        ├── ResearchAgent                      ├── ResearchAgent
        ├── RetrievalAgent                     ├── RetrievalAgent
        ├── InsightAgent                       ├── InsightAgent
        └── AngleAgent ──► [user selects]      ├── (AngleAgent if no angle passed)
                                               ├── OutlineAgent
                                               ├── DraftWriterAgent ──► Draft created
                                               ├── FactCheckerAgent  ──┐
                                               ├── StyleReviewerAgent ─┤
                                               ├── EditorAgent ◄───────┘
                                               └── MediaDirectorAgent (optional)
                                                           │
                                               [human reviews · approves]
                                                           │
                                               PublisherAgent ──► X API v2
```

Every agent result is stored in `agent_traces`:
`agent_name · step_order · input_json · output_json · model_name · token_usage_json · latency_ms`

---

### Model Routing

`LLMService` selects model tier based on `agent_name`:

| Tier | Agents | Default Model |
|------|--------|---------------|
| **Strong** | `insight_agent`, `angle_agent`, `draft_writer_agent`, `editor_agent` | `gpt-5.5` |
| **Cheap** | `research_agent`, `outline_agent`, `fact_checker_agent`, `style_reviewer_agent`, `media_director_agent` | `gpt-5.4-mini` |

Override: `OPENAI_MODEL_STRONG` and `OPENAI_MODEL_CHEAP` in `.env`.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, TanStack Query |
| UI | Custom design system, IBM Plex Mono, Inter |
| Backend | FastAPI 0.115, Pydantic v2, SQLAlchemy 2.x async, Alembic |
| Task queue | Celery 5, Redis broker + result backend |
| Database | PostgreSQL 16 (pgvector optional) |
| Cache | Redis 7 |
| LLM | OpenAI `gpt-5.5` / `gpt-5.4-mini` |
| Image | OpenAI `gpt-image-2` |
| Speech-to-text | OpenAI `gpt-4o-transcribe` / `gpt-4o-mini-transcribe` |
| Text-to-speech | OpenAI `gpt-4o-mini-tts` |
| Embeddings | `text-embedding-3-small` |
| X publishing | X API v2, OAuth 2.0 PKCE |
| Reverse proxy | nginx |
| Containers | Docker, Docker Compose |
| Hosting | DigitalOcean — Ubuntu 22.04, 2 vCPU, 2 GB RAM |

---

## Content Types

| Type | Generation | X publish method |
|------|-----------|----------------|
| `text_post` | Single `text` field | `POST /2/tweets` |
| `thread` | `thread_items[]` array | Reply chain via `reply.in_reply_to_tweet_id` |
| `quote_retweet` | `text` + `quote_url` | Post with quote URL or copy-ready draft |
| `image_post` | `text` + generated image | `media_id` attached to tweet |
| `carousel` | Up to 4 images | Up to 4 `media_ids` on a single tweet |
| `voice_video` | TTS + captions + background → MP4 | Chunked video upload → `media_id` |
| `research_article` | Long-form `text` | Thread or single post |

---

## Data Model

```
users
  id · email · password_hash · full_name · created_at

connected_accounts
  id · user_id · provider(x)
  access_token_encrypted · refresh_token_encrypted
  scopes · expires_at

content_projects
  id · user_id · title · topic · goal · target_audience
  status: draft | researching | generating | ready | published | failed

sources
  id · project_id · source_type · url · title · snippet
  credibility_score · extracted_text · summary

drafts
  id · project_id · user_id · type · status
  text · thread_items(jsonb) · title
  fact_check_score · style_score · quality_score
  x_post_id · published_at · scheduled_at

fact_checks
  id · draft_id · claim · verdict
  confidence · evidence(jsonb) · suggested_fix

media_assets
  id · draft_id · user_id · type · file_url · storage_key
  mime_type · size_bytes · duration_seconds
  x_media_id · status: pending | generating | ready | uploaded_to_x | failed

agent_traces
  id · project_id · draft_id · agent_name · step_order
  input_json · output_json · model_name
  token_usage_json · latency_ms

publish_jobs
  id · draft_id · user_id · platform(x) · status
  scheduled_at · published_at · platform_post_id
  error_message · attempts

writing_samples
  id · user_id · title · text · source_type · embedding_id
```

---

## API Reference

### Authentication
```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
GET    /api/v1/auth/me
POST   /api/v1/auth/logout
```

### X OAuth
```
GET    /api/v1/x/connect          → redirect to X OAuth screen
GET    /api/v1/x/callback         → exchange code, store encrypted tokens
GET    /api/v1/x/status
DELETE /api/v1/x/disconnect
```

### Projects & Agents
```
POST   /api/v1/projects
GET    /api/v1/projects
GET    /api/v1/projects/{id}
PATCH  /api/v1/projects/{id}
DELETE /api/v1/projects/{id}

POST   /api/v1/projects/{id}/research          ResearchAgent
POST   /api/v1/projects/{id}/angles            Research → Insight → Angle
POST   /api/v1/projects/{id}/drafts/generate   full 10-agent workflow
GET    /api/v1/projects/{id}/traces
```

### Drafts
```
GET    /api/v1/drafts/{id}
PATCH  /api/v1/drafts/{id}
POST   /api/v1/drafts/{id}/fact-check          re-run FactCheckerAgent
POST   /api/v1/drafts/{id}/revise              EditorAgent + instructions
POST   /api/v1/drafts/{id}/approve
POST   /api/v1/drafts/{id}/publish/x           PublisherAgent
POST   /api/v1/drafts/{id}/schedule/x
```

### Media
```
POST   /api/v1/media/generate-image
POST   /api/v1/media/generate-carousel
POST   /api/v1/media/generate-voice-video
GET    /api/v1/media?draft_id={id}
GET    /api/v1/media/{asset_id}
```

### RAG / Writing Samples
```
GET    /api/v1/rag/writing-samples
POST   /api/v1/rag/writing-samples
GET    /api/v1/rag/sources
POST   /api/v1/rag/sources
```

Interactive docs at `http://localhost:8000/docs`

---

## Local Development

### Prerequisites

- Docker Desktop (or Docker Engine + Compose plugin)
- Node.js 20+ for frontend hot-reload
- Python 3.12+ to run the backend outside Docker

### 1. Clone

```bash
git clone https://github.com/YOUR_USERNAME/nfactorial.git
cd nfactorial
```

### 2. Configure environment

```bash
cp backend/.env.example backend/.env
```

`MOCK_MODE=true` is the safe default — no real API keys needed for local work.

To test real AI output:

```env
MOCK_MODE=false
OPENAI_API_KEY=sk-...

# X publishing (optional for local dev)
ENABLE_REAL_X_API=true
X_CLIENT_ID=...
X_CLIENT_SECRET=...
X_REDIRECT_URI=http://localhost:8000/api/v1/x/callback
```

### 3. Start services

```bash
# Infrastructure only
docker compose up -d postgres redis

# Full stack
docker compose up -d
```

### 4. Backend without Docker

```bash
cd backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### 5. Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

Vite proxies `/api` to `localhost:8000` automatically.

### 6. Tests

```bash
cd backend
pytest -v
# Tests run with MOCK_MODE=true — no API keys needed
```

---

## Production Deployment

The production environment runs on a **DigitalOcean Droplet** (Ubuntu 22.04 LTS, **2 vCPU, 2 GB RAM**) with Docker Compose, nginx reverse proxy, and Let's Encrypt SSL.

### 1. Provision the server

```bash
# SSH into the fresh droplet
ssh root@YOUR_DROPLET_IP

# Install Docker & tools
curl -fsSL https://get.docker.com | sh
apt-get install -y docker-compose-plugin nginx certbot python3-certbot-nginx git

# Clone
git clone https://github.com/YOUR_USERNAME/nfactorial.git /root/x-ai
cd /root/x-ai
```

### 2. Configure secrets

```bash
cp backend/.env.example backend/.env
nano backend/.env
```

Critical production settings:

```env
ENVIRONMENT=production
MOCK_MODE=false
SECRET_KEY=<64-char random hex>
OPENAI_API_KEY=sk-...

# Enable real providers
ENABLE_REAL_IMAGE_GENERATION=true
ENABLE_REAL_STT=true
ENABLE_REAL_TTS=true
ENABLE_REAL_WEB_SEARCH=true
DEFAULT_IMAGE_PROVIDER=openai
DEFAULT_AUDIO_PROVIDER=openai
DEFAULT_SEARCH_PROVIDER=openai

# X OAuth
ENABLE_REAL_X_API=true
X_CLIENT_ID=...
X_CLIENT_SECRET=...
X_REDIRECT_URI=https://yourdomain.com/api/v1/x/callback

CORS_ORIGINS=["https://yourdomain.com"]

# Resource limits for 2 GB RAM
CELERY_WORKER_CONCURRENCY=1
MAX_CONCURRENT_GENERATIONS=1
```

### 3. X Developer Portal

In [developer.twitter.com](https://developer.twitter.com) → your app → **App settings → User authentication settings → Callback URI**:

```
https://yourdomain.com/api/v1/x/callback
```

### 4. SSL

```bash
certbot --nginx -d yourdomain.com
```

### 5. Deploy

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

### 6. Verify

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs backend --tail=50
curl https://yourdomain.com/api/v1/health
```

### 7. Update

```bash
git pull
docker compose -f docker-compose.prod.yml up -d --build backend worker
```

### Resource notes for 2 vCPU / 2 GB

| Setting | Value | Why |
|---------|-------|-----|
| `CELERY_WORKER_CONCURRENCY` | `1` | Avoids OOM on heavy agent runs |
| `MAX_CONCURRENT_GENERATIONS` | `1` | Serialises LLM calls |
| Redis `maxmemory` | `256mb` | Leaves headroom for Postgres |
| Gunicorn workers | `2` | Matches vCPU count |

For concurrent image generation (`gpt-image-2`), consider upgrading to a 4 GB droplet.

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MOCK_MODE` | `true` | All providers return mocks; no API keys needed |
| `ENVIRONMENT` | `development` | `production` enables stricter error handling |
| `SECRET_KEY` | — | JWT signing key, 64-char hex minimum |
| `OPENAI_API_KEY` | — | Required when `MOCK_MODE=false` |
| `OPENAI_MODEL_STRONG` | `gpt-5.5` | Strong-tier agents (writer, editor, insight) |
| `OPENAI_MODEL_CHEAP` | `gpt-5.4-mini` | Cheap-tier agents (research, fact-check, style) |
| `OPENAI_IMAGE_MODEL` | `gpt-image-2` | Image generation model |
| `ENABLE_REAL_IMAGE_GENERATION` | `false` | Enables OpenAI image generation |
| `ENABLE_REAL_STT` | `false` | Enables OpenAI speech-to-text |
| `ENABLE_REAL_TTS` | `false` | Enables OpenAI text-to-speech |
| `ENABLE_REAL_WEB_SEARCH` | `false` | Enables live web search |
| `ENABLE_REAL_X_API` | `false` | Enables publishing to real X account |
| `X_CLIENT_ID` | — | X Developer app OAuth Client ID |
| `X_CLIENT_SECRET` | — | X Developer app OAuth Client Secret |
| `X_REDIRECT_URI` | — | Must match X Developer Portal callback URI exactly |
| `STORAGE_PROVIDER` | `local` | `local` or `s3` |
| `S3_BUCKET` | — | Required when `STORAGE_PROVIDER=s3` |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | Allowed origins — JSON array |
| `DATABASE_URL` | `postgresql+asyncpg://...` | Async PostgreSQL DSN |
| `REDIS_URL` | `redis://...` | Redis connection string |
| `CELERY_WORKER_CONCURRENCY` | `1` | Celery worker process count |

Full reference: `backend/.env.example`

---

## Security

- **Token encryption** — X OAuth access and refresh tokens are AES-256 encrypted at rest. Raw tokens are never returned to the frontend or written to logs.
- **Publish gate** — `PublisherAgent` checks `draft.status == "approved"` before every X API call. There is no API path to bypass this check in the default configuration.
- **JWT secrets** — must be set via environment variable, never hardcoded.
- **File uploads** — stored in a private bucket or local path; signed URLs generated per-request.
- **Audit trail** — every publish attempt (success or failure) is logged in `publish_jobs` with request details and error messages.
- **`.env` is gitignored** — never commit secrets.

---

## Project Structure

```
nfactorial/
├── backend/
│   ├── app/
│   │   ├── agents/                  Agent implementations
│   │   │   ├── base.py              BaseAgent, AgentContext, AgentResult
│   │   │   ├── workflow.py          ContentWorkflow orchestrator
│   │   │   ├── research_agent.py
│   │   │   ├── retrieval_agent.py
│   │   │   ├── insight_agent.py
│   │   │   ├── angle_agent.py
│   │   │   ├── outline_agent.py
│   │   │   ├── draft_writer_agent.py
│   │   │   ├── fact_checker_agent.py
│   │   │   ├── style_reviewer_agent.py
│   │   │   ├── editor_agent.py
│   │   │   ├── media_director_agent.py
│   │   │   └── publisher_agent.py
│   │   ├── api/v1/endpoints/        REST route handlers
│   │   ├── core/                    Config, security, encryption, logging
│   │   ├── db/                      Session factory, base declarative
│   │   ├── models/                  SQLAlchemy ORM models
│   │   ├── providers/
│   │   │   ├── llm/                 OpenAI, Anthropic, mock LLM providers
│   │   │   ├── media/               Image, audio, video, mock providers
│   │   │   ├── search/              Web search provider
│   │   │   └── storage/             S3 and local file storage
│   │   ├── schemas/                 Pydantic request/response schemas
│   │   ├── services/                Business logic
│   │   └── workers/                 Celery tasks
│   ├── alembic/                     Database migrations
│   └── tests/
├── frontend/
│   └── src/
│       ├── components/              Reusable UI components
│       ├── hooks/                   TanStack Query data hooks
│       ├── lib/                     API client, auth utilities
│       ├── pages/                   Route-level pages
│       └── types/                   TypeScript type definitions
├── nginx/                           Reverse proxy configuration
├── docker-compose.yml               Local development stack
├── docker-compose.prod.yml          Production stack
└── CLAUDE.md                        Full product and architecture specification
```

---

## Demo Flow

1. **Register** and complete the 3-step onboarding (brand voice, writing samples, X connection).
2. **New Project** — enter a topic, goal, and target audience.
3. **Research** — `ResearchAgent` surfaces findings, contradictions, and source quality.
4. **Angles** — review 5 generated angles, each with thesis, hook, and risk score.
5. **Select an angle** — the full 10-agent pipeline runs automatically.
6. **Composer** — edit the draft; use "Make sharper", "Improve hook", "Fact Check" actions.
7. **Agent Traces** — inspect every step: input, output, model, tokens, latency.
8. **Approve** — click "Approve & Publish" once the quality gate passes.
9. **Published** — the platform posts to X and returns the tweet URL or detailed error.

---

<div align="center">

Built as an assignment project at **nfactorial** school.  
Deployed on DigitalOcean · Powered by OpenAI · Publishes to X/Twitter.

</div>
