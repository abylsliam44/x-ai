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

## Setup

### Prerequisites

- Node.js 18+
- Backend running at `http://localhost:8000`

### Install

```bash
cd frontend
npm install
```

### Configure

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Default:
```
VITE_API_BASE_URL=http://localhost:8000
```

### Run

```bash
npm run dev
# Opens at http://localhost:5173
```

### Build

```bash
npm run build
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

## Key Features

- **Agent traces panel** — expandable timeline of all agent steps
- **Fact check panel** — verdict per claim with confidence ring
- **X preview** — real-time X thread preview
- **Style panel** — one-click Editor Agent revisions
- **Approve → Publish gate** — publish only after explicit approval
- **Mock mode banner** — shows when backend is in mock mode

## API

The frontend proxies all `/api` requests to `http://localhost:8000` via Vite's dev proxy.

JWT tokens are stored in `localStorage` for MVP.

## X OAuth Flow

1. Click "Connect X Account" in Settings → X Connection
2. Backend returns OAuth URL (`GET /api/v1/x/connect`)
3. User authorizes in popup window
4. Callback processed by backend (`GET /api/v1/x/callback`)
5. Status refreshes automatically

## Notes

- Voice content is explained as video: "Voice content is published to X as a video with audio, captions, and visual background."
- All UI copy is English only
- Mock mode shows a banner at the top when `mock_mode=true` in health response
