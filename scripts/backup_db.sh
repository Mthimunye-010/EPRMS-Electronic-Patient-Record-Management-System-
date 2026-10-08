#!/usr/bin/env bash
# Create an encrypted PostgreSQL custom-format backup using age.
# Requires DJANGO_DB_* connection variables, AGE_RECIPIENT, pg_dump and age.

set -euo pipefail
umask 077

: "${DJANGO_DB_PASSWORD:?Set DJANGO_DB_PASSWORD before creating a backup.}"
: "${AGE_RECIPIENT:?Set AGE_RECIPIENT to the public age key for the backup custodian.}"

command -v pg_dump >/dev/null || { echo "pg_dump is required." >&2; exit 1; }
command -v age >/dev/null || { echo "age is required." >&2; exit 1; }

DB_NAME="${DJANGO_DB_NAME:-eprms_db}"
DB_USER="${DJANGO_DB_USER:-eprms_user}"
DB_HOST="${DJANGO_DB_HOST:-localhost}"
DB_PORT="${DJANGO_DB_PORT:-5432}"
DB_SSLMODE="${DJANGO_DB_SSLMODE:-}"
DB_SSLROOTCERT="${DJANGO_DB_SSLROOTCERT:-}"
if [[ "$DB_HOST" != "localhost" && "$DB_HOST" != "127.0.0.1" && "$DB_HOST" != "::1" ]]; then
  [[ "$DB_SSLMODE" == "verify-full" && -n "$DB_SSLROOTCERT" ]] || {
    echo "Remote database backups require DJANGO_DB_SSLMODE=verify-full and DJANGO_DB_SSLROOTCERT." >&2
    exit 1
  }
  export PGSSLMODE="$DB_SSLMODE" PGSSLROOTCERT="$DB_SSLROOTCERT"
fi
BACKUP_DIR="$(dirname "$0")/../backups"
mkdir -p "$BACKUP_DIR"

TIMESTAMP="$(date +"%Y%m%d_%H%M%S")"
BACKUP_FILE="$BACKUP_DIR/eprms_backup_${TIMESTAMP}.dump.age"
TEMP_FILE="$(mktemp "$BACKUP_DIR/.eprms_backup_XXXXXX.dump")"
TEMP_ENCRYPTED="$(mktemp "$BACKUP_DIR/.eprms_backup_XXXXXX.dump.age")"
trap 'rm -f -- "$TEMP_FILE" "$TEMP_ENCRYPTED"' EXIT

echo "Creating encrypted backup for '$DB_NAME'..."
PGPASSWORD="$DJANGO_DB_PASSWORD" pg_dump \
  -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
  -F c -f "$TEMP_FILE"
age --recipient "$AGE_RECIPIENT" "$TEMP_FILE" > "$TEMP_ENCRYPTED"
mv -- "$TEMP_ENCRYPTED" "$BACKUP_FILE"
rm -f -- "$TEMP_FILE"
rm -f -- "$TEMP_ENCRYPTED"
trap - EXIT

# Keep only the 14 most recent encrypted backups.
find "$BACKUP_DIR" -maxdepth 1 -type f -name 'eprms_backup_*.dump.age' \
  -printf '%T@ %p\0' | sort -zrn | tail -z -n +15 | cut -z -d' ' -f2- | xargs -0 -r rm --
echo "Encrypted backup complete: $BACKUP_FILE"
