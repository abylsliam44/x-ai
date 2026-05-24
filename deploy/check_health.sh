#!/usr/bin/env bash
# check_health.sh — verify all production services are running correctly.
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

PASS=0
FAIL=0

check() {
  local label="$1"
  local cmd="$2"
  if eval "$cmd" > /dev/null 2>&1; then
    echo "  [OK]  $label"
    PASS=$((PASS + 1))
  else
    echo "  [FAIL] $label"
    FAIL=$((FAIL + 1))
  fi
}

echo "==> Docker service states:"
docker compose -f docker-compose.prod.yml ps --format "table {{.Name}}\t{{.Status}}"

echo ""
echo "==> Health checks:"
check "HTTP /health endpoint"        "curl -sf http://localhost/health"
check "API /api/v1/health endpoint"  "curl -sf http://localhost/api/v1/health"
check "backend direct health"        "docker compose -f docker-compose.prod.yml exec -T backend curl -sf http://localhost:8000/api/v1/health"
check "postgres container healthy"   "docker compose -f docker-compose.prod.yml exec -T postgres pg_isready -U postgres"
check "redis container healthy"      "docker compose -f docker-compose.prod.yml exec -T redis redis-cli ping"
check "backend container running"    "docker compose -f docker-compose.prod.yml exec -T backend echo ok"
check "worker container running"     "docker compose -f docker-compose.prod.yml exec -T worker celery -A app.workers.celery_app.celery_app inspect ping -t 5"

echo ""
echo "==> Disk usage:"
df -h / | tail -1

echo ""
echo "==> Memory:"
free -h

echo ""
if [ "$FAIL" -eq 0 ]; then
  echo "All $PASS checks passed."
else
  echo "$FAIL check(s) FAILED, $PASS passed."
  exit 1
fi
