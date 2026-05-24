#!/usr/bin/env bash
# backup_db.sh — dump the production PostgreSQL database.
# Creates a timestamped .sql.gz in ./backups/
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

BACKUP_DIR="$PROJECT_ROOT/backups"
mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/agentic_x_${TIMESTAMP}.sql.gz"

echo "==> Backing up database to $BACKUP_FILE ..."
docker compose -f docker-compose.prod.yml exec -T postgres \
  pg_dump -U postgres agentic_x | gzip > "$BACKUP_FILE"

echo "    Done. File size: $(du -sh "$BACKUP_FILE" | cut -f1)"

# Keep only the 10 most recent backups
echo "==> Pruning old backups (keeping 10 most recent)..."
ls -t "$BACKUP_DIR"/*.sql.gz 2>/dev/null | tail -n +11 | xargs -r rm --
echo "    Backups remaining: $(ls "$BACKUP_DIR"/*.sql.gz 2>/dev/null | wc -l)"
