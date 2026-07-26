#!/bin/bash
set -e

echo "=== Deploying scrapers to VPS ==="
VPS="149.56.46.173"
REMOTE_PATH="/home/ubuntu/sdc"

echo "1. Syncing project files..."
rsync -avz --delete \
  "$(dirname "$0")/../scrapers/" \
  "ubuntu@$VPS:$REMOTE_PATH/scrapers/"
rsync -avz \
  "$(dirname "$0")/../data/abe-music.json" \
  "ubuntu@$VPS:$REMOTE_PATH/data/abe-music.json"

echo "2. Deploying docker compose (Playwright MCP)..."
ssh "ubuntu@$VPS" "cd $REMOTE_PATH/scrapers && docker compose -f docker-compose.scrapers.yml up -d"

echo "3. Checking health..."
sleep 5
ssh "ubuntu@$VPS" "curl -s http://localhost:8931/health && echo ' playwright OK' || echo ' playwright FAIL'"

echo "4. Installing sync cron (every 6h)..."
ssh "ubuntu@$VPS" "cd $REMOTE_PATH && bash scripts/install-sync-cron.sh"

echo "5. Running initial sync..."
ssh "ubuntu@$VPS" "cd $REMOTE_PATH && python3 -m scrapers.sync"

echo "=== Deploy complete ==="
