#!/bin/bash
# Mystika Deploy Script
# Run from CI/CD or locally to deploy to OVH server

set -e

SERVER="ubuntu@149.56.46.173"
REMOTE_DIR="/home/ubuntu/mystika"
LOCAL_DIR="/home/mystic/sonora-digital-corp/products/mystika"

echo "🚀 Deploying Mystika to $SERVER"

# 1. Build web
echo "📦 Building web..."
cd "$LOCAL_DIR/web"
npm run build

# 2. Rsync to server
echo "📤 Uploading files..."
rsync -avz --delete \
  --exclude 'node_modules' \
  --exclude '.next/cache' \
  --exclude '.git' \
  "$LOCAL_DIR/" "$SERVER:$REMOTE_DIR/"

# 3. Install deps on server
echo "🔧 Installing dependencies..."
ssh "$SERVER" "
  cd $REMOTE_DIR/api && npm install --production
  cd $REMOTE_DIR/telegram-bot && npm install --production
  cd $REMOTE_DIR/web && npm install --production
"

# 4. Run DB migration
echo "🗄️ Running migrations..."
ssh "$SERVER" "cd $REMOTE_DIR/api && node db/migrate.js"

# 5. Restart services
echo "🔄 Restarting services..."
ssh "$SERVER" "
  sudo systemctl daemon-reload
  sudo systemctl restart mystika-api
  sudo systemctl restart mystika-web
  sudo systemctl restart mystika-bot
  sudo systemctl reload nginx
"

echo "✅ Mystika deployed successfully!"
echo "🌐 https://mystika.app"
