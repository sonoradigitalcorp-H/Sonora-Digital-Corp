#!/bin/sh
# Twenty CRM entrypoint — with timeouts for hanging commands
set -e

# Check if core schema exists
has_schema=$(psql -tAc "SELECT EXISTS (SELECT 1 FROM information_schema.schemata WHERE schema_name = 'core')" ${PG_DATABASE_URL})
if [ "$has_schema" = "f" ]; then
    echo "Database empty, running migrations..."
    yarn database:init:prod
fi

# Run with timeouts — these commands hang if server not up
timeout 15 yarn command:prod cache:flush 2>/dev/null || echo "cache:flush skipped (timeout)"
timeout 15 yarn command:prod upgrade 2>/dev/null || echo "upgrade skipped (timeout)"
timeout 10 yarn command:prod cron:register:all 2>/dev/null || echo "cron:register skipped (timeout)"

echo "Starting Twenty CRM server..."
exec node dist/main
