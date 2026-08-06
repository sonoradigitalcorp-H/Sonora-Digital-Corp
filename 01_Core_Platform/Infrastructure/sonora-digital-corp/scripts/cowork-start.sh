#!/bin/bash
# SDC Cowork Automation — Morning Routine
# Runs at session start to set up everything

echo "🚀 Starting SDC Cowork Automation..."

# 1. Check OpenClaw gateway
if curl -s http://localhost:18789/health | grep -q '"ok":true'; then
    echo "✅ OpenClaw gateway: ONLINE"
else
    echo "⚠️  OpenClaw gateway: OFFLINE - starting..."
    nohup openclaw gateway > /tmp/openclaw.log 2>&1 &
    sleep 3
fi

# 2. Check Docker services
echo "📦 Service Status:"
docker ps --format "  {{.Names}}: {{.Status}}" 2>/dev/null

# 3. Check git status
echo "📋 Git Status:"
cd /home/mystic/Documentos/Sonora\ Digital\ Corp/sonora-digital-corp 2>/dev/null
git status --short 2>/dev/null | head -5
echo "  Last commit: $(git log --oneline -1 2>/dev/null)"

# 4. Run pre-flight check
echo "🔍 Preflight Check:"
python3 scripts/preflight.py --skip-docker --skip-git 2>/dev/null | tail -5

# 5. Check engram memory
echo "🧠 Memory Status:"
python3 -c "
import requests
try:
    r = requests.get('http://localhost:18789/health')
    print(f'  OpenClaw: {r.json()}')
except: print('  OpenClaw: unreachable')
" 2>/dev/null

echo "✅ SDC Cowork Automation Complete"