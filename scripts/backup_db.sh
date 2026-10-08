#!/usr/bin/env bash
# Simple PostgreSQL backup script for the EPRMS database.
# Addresses the project scope requirement for a data backup/recovery strategy.
#
# Usage: ./scripts/backup_db.sh
# Requires the same DJANGO_DB_* environment variables used by the app
# (see .env.example), plus the `pg_dump` client tool installed locally.

set -euo pipefail

DB_NAME="${DJANGO_DB_NAME:-eprms_db}"
DB_USER="${DJANGO_DB_USER:-eprms_user}"
DB_HOST="${DJANGO_DB_HOST:-localhost}"
DB_PORT="${DJANGO_DB_PORT:-5432}"

BACKUP_DIR="$(dirname "$0")/../backups"
mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/eprms_backup_${TIMESTAMP}.sql"

echo "Backing up database '$DB_NAME' to $BACKUP_FILE ..."
PGPASSWORD="${DJANGO_DB_PASSWORD:-}" pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -F c -f "$BACKUP_FILE"
echo "Backup complete."

# Keep only the 14 most recent backups
ls -1t "$BACKUP_DIR"/eprms_backup_*.sql 2>/dev/null | tail -n +15 | xargs -r rm --
