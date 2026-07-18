#!/usr/bin/env bash
# Sync repo from laptop to VPS + regenerate configs + restart services
set -euo pipefail

echo "=== Syncing to VPS ==="
cd "$(dirname "$0")/.."

# Push to GitHub (trigger VPS sync via GitHub Action)
if git diff --quiet && git diff --cached --quiet; then
    echo "No changes to push"
else
    echo "Changes detected — committing and pushing..."
    git add -A
    git commit -m "sync: $(date '+%Y-%m-%d %H:%M')"
    git push origin main
    echo "Pushed to GitHub — VPS will auto-sync via GitHub Action"
fi

# Also sync directly to VPS
echo "Direct sync to VPS..."
rsync -avz --exclude '.git' --exclude 'node_modules' --exclude '__pycache__' --exclude '*.db' \
    --exclude '.env*' --exclude 'state/events/*.jsonl' \
    . ubuntu@149.56.46.173:/home/ubuntu/sonora-digital-corp/

echo "Regenerating configs on VPS..."
ssh ovh "cd /home/ubuntu/sonora-digital-corp && python3 scripts/generate-configs.py"

echo "Building Call Engine on VPS..."
ssh ovh "cd /home/ubuntu/sonora-digital-corp/call-engine && go build -o /home/ubuntu/.local/bin/call-engine ./cmd/converse" 2>/dev/null && echo "  ✅ Call Engine built" || echo "  ⚠️  Call Engine build skipped"

echo "Restarting Guardian..."
ssh ovh "sudo systemctl restart truth-guardian.service 2>/dev/null || sudo kill -9 \$(pgrep -f guardian.main) 2>/dev/null; sleep 1; sudo systemctl start truth-guardian.service 2>/dev/null &"

echo "=== Sync complete ==="
