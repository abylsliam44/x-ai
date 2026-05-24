#!/usr/bin/env bash
# restore_db.sh — restore a PostgreSQL backup.
# Usage: ./deploy/restore_db.sh <path-to-backup.sql.gz>
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

BACKUP_FILE="${1:-}"
if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: $0 <backup-file.sql.gz>"
  exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
  echo "ERROR: File not found: $BACKUP_FILE"
  exit 1
fi

echo "WARNING: This will DROP and recreate the agentic_x database."
read -r -p "Type 'yes' to confirm: " confirm
if [ "$confirm" != "yes" ]; then
  echo "Aborted."
  exit 0
fi

echo "==> Dropping and recreating database..."
docker compose -f docker-compose.prod.yml exec -T postgres \
  psql -U postgres -c "DROP DATABASE IF EXISTS agentic_x;"
docker compose -f docker-compose.prod.yml exec -T postgres \
  psql -U postgres -c "CREATE DATABASE agentic_x;"

echo "==> Restoring from $BACKUP_FILE ..."
gunzip -c "$BACKUP_FILE" | docker compose -f docker-compose.prod.yml exec -T postgres \
  psql -U postgres agentic_x

echo "==> Running migrations to ensure schema is current..."
docker compose -f docker-compose.prod.yml exec -T backend alembic upgrade head

echo "    Restore complete."
