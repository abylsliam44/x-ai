# nfactorial X Content — Frontend

Production-ready React frontend for the Agentic X Content Platform.

## Stack

- **React 18** + **TypeScript**
- **Vite** (build tool)
- **Tailwind CSS** (design tokens from ZIP prototype)
- **React Router v6** (routing)
- **TanStack Query v5** (data fetching + cache)
- **date-fns** (date formatting)

## Design

The visual language is adapted from the Claude Design ZIP prototype:

- Pure black/dark background (`#000` / `#0a0a0a` / `#111`)
- White primary actions
- IBM Plex Mono for all data labels
- Inter for UI text
- Pill-shaped buttons
- Stage-based workflow tabs

## Prerequisites

- **Node.js 18+** — or use Docker (see below)
- **Backend running** at `http://localhost:8000`

## Setup

### With Node.js installed

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
# Opens at http://localhost:5173
```

### With Docker (no local Node.js required)

```bash
# Install dependencies
docker run --rm -v "$(pwd)":/app -w /app node:20-alpine npm install

# Start dev server
docker run --rm -d --name nfactorial-dev \
  -p 5173:5173 \
  -v "$(pwd)":/app -w /app \
  node:20-alpine sh -c "npm run dev -- --host 0.0.0.0"

# Production build
docker run --rm -v "$(pwd)":/app -w /app node:20-alpine npm run build
```

### Configure

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Default `.env`:
```
VITE_API_BASE_URL=http://localhost:8000
```

The Vite dev proxy forwards all `/api` requests to the backend.

## Backend

Start the backend (PostgreSQL + Redis + FastAPI):

```bash
cd backend
docker compose up -d --build
# Backend available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

## Screens

| Route | Screen |
|-------|--------|
| `/login` | Login |
| `/register` | Register |
| `/dashboard` | Project list |
| `/projects/new` | 3-step project wizard |
| `/projects/:id` | Workspace with 6-stage pipeline |
| `/settings` | X connection, writing samples, brand voice |

## Workflow

```
Sources → Insights → Angles → Draft → Review → Publish
```

Each stage connects to the backend API.

## End-to-End Test Flow (Mock Mode)

The backend runs in `mock_mode=true` by default — all AI agents return deterministic mock responses, no API keys required.

1. **Register** — go to `/register`, create an account
2. **Login** — redirects to `/dashboard`
3. **Create project** — click "New Project", fill in topic + goal
4. **Add source** — in the workspace Sources tab, click "Add Source" and add a URL or text
5. **Generate angles** — click "Generate Angles →" at the bottom of Sources tab (or the topbar button)
6. **Select angle** — click an angle card in the Angles tab
7. **Generate draft** — in the Draft tab, choose a format and click "Generate Draft"
8. **Fact check** — switch to the Fact Check panel in the right sidebar
9. **Revise** — use the quick-action buttons (Improve Hook, Make Shorter, etc.) or type custom instructions
10. **Approve** — click "Approve" in the topbar (requires draft to be in `ready_for_review` status)
11. **Connect X (mock)** — go to Settings → X Connection → Connect X Account; the mock OAuth popup completes automatically
12. **Publish** — navigate to the Publish stage, click "Publish to X" → confirm in the modal

The published result shows `mock_post_<id>` since backend is in mock mode.

## Key Features

- **Agent traces panel** — expandable timeline of all agent steps with input/output JSON
- **Fact check panel** — verdict per claim with confidence ring visualization
- **X preview** — real-time X thread preview with avatar and thread line
- **Style panel** — one-click Editor Agent revisions
- **Approve → Publish gate** — publish only after explicit approval
- **Mock mode banner** — shown when backend is in mock mode
- **X OAuth polling** — status refreshes automatically after popup closes

## API

The frontend proxies all `/api` requests to `http://localhost:8000` via Vite's dev proxy.

JWT tokens are stored in `localStorage` for MVP.

## X OAuth Flow

1. Click "Connect X Account" in Settings → X Connection (or the Publish stage)
2. Backend returns OAuth URL (`GET /api/v1/x/connect`)
3. URL opens in a popup window
4. In mock mode, the popup's URL is the callback URL itself — account connects immediately
5. Frontend polls `GET /api/v1/x/status` every 1.5s until `connected: true`
6. Status refreshes, popup closes automatically

## Notes

- Voice content is published to X as a video with audio, captions, and visual background
- All UI copy is English only
- Mock mode shows a banner at the top when `mock_mode=true` in the health response
- Brand Voice tab in Settings is UI-only in MVP (backend storage coming post-MVP)
