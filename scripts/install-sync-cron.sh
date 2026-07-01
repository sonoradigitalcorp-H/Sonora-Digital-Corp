#!/bin/bash
# Installs the data sync cron job (every 6 hours)
set -e

SDC_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CRON_EXPR="0 */6 * * * cd $SDC_DIR && python3 -m scrapers.sync >> $SDC_DIR/logs/sync.log 2>&1"

# Check if already installed
if crontab -l 2>/dev/null | grep -q "scrapers.sync"; then
    echo "Sync cron already installed. Updating..."
    crontab -l 2>/dev/null | grep -v "scrapers.sync" | { cat; echo "$CRON_EXPR"; } | crontab -
else
    echo "Installing sync cron..."
    (crontab -l 2>/dev/null; echo "$CRON_EXPR") | crontab -
fi

echo "Sync cron installed. Runs every 6 hours."
echo "Logs: $SDC_DIR/logs/sync.log"
crontab -l | grep scrapers
