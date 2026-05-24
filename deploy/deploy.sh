#!/usr/bin/env bash
# deploy.sh — build and (re)start the production stack.
# Run from the project root: ./deploy/deploy.sh
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# ---------- Pre-flight checks ----------
echo "==> Checking prerequisites..."

if [ ! -f backend/.env ]; then
  echo "ERROR: backend/.env not found. Copy backend/.env.production.example → backend/.env and fill in secrets."
  exit 1
fi

# Ensure required secrets are not empty placeholders
REQUIRED_VARS=(SECRET_KEY OPENAI_API_KEY)
for var in "${REQUIRED_VARS[@]}"; do
  val=$(grep -E "^${var}=" backend/.env | cut -d= -f2- | tr -d '"' || true)
  if [ -z "$val" ] || [[ "$val" == *"change-me"* ]] || [[ "$val" == *"FILL"* ]]; then
    echo "ERROR: ${var} in backend/.env is empty or still a placeholder. Fill it before deploying."
    exit 1
  fi
done

# ---------- Build frontend ----------
echo "==> Building frontend..."
if [ -d frontend/node_modules ]; then
  docker run --rm \
    -v "$PROJECT_ROOT/frontend":/app \
    -w /app \
    -e VITE_API_BASE_URL=/api \
    node:20-alpine \
    sh -c "npm ci --silent && npm run build"
else
  docker run --rm \
    -v "$PROJECT_ROOT/frontend":/app \
    -w /app \
    -e VITE_API_BASE_URL=/api \
    node:20-alpine \
    sh -c "npm install --silent && npm run build"
fi
echo "    Frontend built → frontend/dist/"

# ---------- Pull / build containers ----------
echo "==> Building Docker images..."
docker compose -f docker-compose.prod.yml build --pull

# ---------- Start services ----------
echo "==> Starting services..."
docker compose -f docker-compose.prod.yml up -d

# ---------- Run migrations ----------
echo "==> Running database migrations..."
docker compose -f docker-compose.prod.yml exec -T backend alembic upgrade head

# ---------- Health check ----------
echo "==> Waiting for backend health..."
for i in $(seq 1 12); do
  if curl -sf http://localhost/health > /dev/null 2>&1; then
    echo "    Backend is healthy."
    break
  fi
  echo "    Attempt $i/12 — waiting 5s..."
  sleep 5
done

if ! curl -sf http://localhost/health > /dev/null 2>&1; then
  echo "ERROR: Backend did not become healthy after 60s. Check logs:"
  echo "  docker compose -f docker-compose.prod.yml logs backend"
  exit 1
fi

echo ""
echo "==> Deployment complete. Stack is running."
echo "    Logs: docker compose -f docker-compose.prod.yml logs -f"
