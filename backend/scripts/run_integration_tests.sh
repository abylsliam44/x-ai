#!/usr/bin/env bash
# ============================================================
# run_integration_tests.sh
#
# Runs the real-provider integration test suite inside the
# running backend Docker container.
#
# Usage (from project root):
#   ./backend/scripts/run_integration_tests.sh [extra pytest args]
#
# Examples:
#   ./backend/scripts/run_integration_tests.sh
#   ./backend/scripts/run_integration_tests.sh -k test_real_angle
#   ./backend/scripts/run_integration_tests.sh -k test_real_media
#   ./backend/scripts/run_integration_tests.sh --no-header -q
#
# Requirements:
#   - backend-backend-1 container is running (docker compose up)
#   - backend-postgres-1 container is running and healthy
#   - backend/.env has real API keys (MOCK_MODE=false)
# ============================================================
set -euo pipefail

BACKEND_CONTAINER="${BACKEND_CONTAINER:-backend-backend-1}"
POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-backend-postgres-1}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
TEST_DB="agentic_x_test"
EXTRA_ARGS="${@:-}"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Integration test suite — real providers (no mocks)"
echo "  Backend   : $BACKEND_CONTAINER"
echo "  Postgres  : $POSTGRES_CONTAINER"
echo "  Test DB   : $TEST_DB"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── 1. Verify containers are running ─────────────────────────────────────────
for C in "$BACKEND_CONTAINER" "$POSTGRES_CONTAINER"; do
  if ! docker ps --format '{{.Names}}' | grep -q "^${C}$"; then
    echo "ERROR: Container '$C' is not running."
    echo "Start the stack first:  docker compose up -d"
    exit 1
  fi
done

# ── 2. Warn if MOCK_MODE=true ─────────────────────────────────────────────────
MOCK_VAL=$(docker exec "$BACKEND_CONTAINER" sh -c \
  "grep -s '^MOCK_MODE=' /app/.env | cut -d= -f2 | tr -d '\"' || echo ''" 2>/dev/null || true)
if [ "$MOCK_VAL" = "true" ]; then
  echo "⚠  WARNING: MOCK_MODE=true in backend/.env"
  echo "   Integration tests override this to false inside the test run."
  echo "   But verify your API keys are present or tests will fail on LLM calls."
  echo ""
fi

# ── 3. Create test database (idempotent) ──────────────────────────────────────
echo "==> Creating test database '$TEST_DB' (if not exists)..."
docker exec "$POSTGRES_CONTAINER" psql -U "$POSTGRES_USER" -tc \
  "SELECT 1 FROM pg_database WHERE datname = '${TEST_DB}';" \
  | grep -q 1 \
  || docker exec "$POSTGRES_CONTAINER" psql -U "$POSTGRES_USER" \
       -c "CREATE DATABASE ${TEST_DB};" > /dev/null
echo "    OK."

# ── 4. Sync integration_tests/ into backend container ────────────────────────
echo "==> Syncing integration_tests/ into container..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
docker cp "$BACKEND_DIR/integration_tests/." "$BACKEND_CONTAINER:/app/integration_tests/"
echo "    Done."

# ── 5. Run the tests ─────────────────────────────────────────────────────────
echo ""
echo "==> Running integration tests..."
echo ""

docker exec -e PYTHONPATH=/app "$BACKEND_CONTAINER" sh -c \
  "cd /app && python -m pytest integration_tests/ $EXTRA_ARGS"
EXIT_CODE=$?

# ── 6. Result ─────────────────────────────────────────────────────────────────
echo ""
if [ $EXIT_CODE -eq 0 ]; then
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "  ✓  All integration tests passed."
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
else
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "  ✗  Some tests failed (exit $EXIT_CODE). See output above."
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

exit $EXIT_CODE
