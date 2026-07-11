#!/bin/sh
set -e

echo "=== Twenty CRM — custom entrypoint ==="

PG_DATABASE_URL="${PG_DATABASE_URL:-postgres://mystik:mystik2026@postgres:5432/mystik}"
TIMEOUT="${TIMEOUT:-120}"

# Check if DB is ready
has_schema=$(psql -tAc "SELECT EXISTS (SELECT 1 FROM information_schema.schemata WHERE schema_name = 'core')" $PG_DATABASE_URL 2>/dev/null || echo "f")

if [ "$has_schema" = "f" ]; then
    echo "Running initial migrations..."
    yarn database:init:prod 2>/dev/null || echo "Init skipped"
fi

# Run upgrade with timeout — avoids hanging
echo "Running upgrade (timeout: ${TIMEOUT}s)..."
timeout $TIMEOUT yarn command:prod cache:flush 2>/dev/null || echo "cache:flush skipped"
timeout $TIMEOUT yarn command:prod upgrade 2>/dev/null || echo "upgrade skipped"
timeout $TIMEOUT yarn command:prod cache:flush 2>/dev/null || echo "cache:flush2 skipped"
timeout $TIMEOUT yarn command:prod cron:register:all 2>/dev/null || echo "cron:register skipped"

echo "Starting server..."
exec "$@"
