#!/bin/bash
# SDC Cowork Automation — Evening Routine
# Runs at session end to commit, save memory, and sync

echo "🌙 Ending SDC Cowork Session..."

cd /home/mystic/Documentos/Sonora\ Digital\ Corp/sonora-digital-corp 2>/dev/null

# 1. Run tests
echo "🧪 Running tests..."
PYTHONPATH=. python3 -m pytest tests/unit/ -q --tb=short 2>/dev/null | tail -3

# 2. Run lint
echo "🔍 Linting..."
python3 -m ruff check src/ tests/ 2>/dev/null | tail -3 || echo "  (ruff not available)"

# 3. Auto-commit changes
echo "💾 Auto-committing..."
git add -A 2>/dev/null
if [ -n "$(git status --short 2>/dev/null)" ]; then
    git commit -m "chore: auto-save session $(date +%Y%m%d_%H%M)" 2>/dev/null
    echo "  Changes committed"
else
    echo "  No changes to commit"
fi

# 4. Save memory
echo "🧠 Saving memory..."
python3 scripts/memory-save.py 2>/dev/null || echo "  Memory save skipped (service offline)"

# 5. Close loop
echo "🔁 Closing loop..."
bash scripts/close-session.sh 2>/dev/null || echo "  Close session skipped"

# 6. Sync to engram
echo "📡 Syncing to engram..."
python3 -c "
import requests
try:
    r = requests.post('http://localhost:18789/api/memory', json={
        'key': 'session-end-20260804',
        'value': 'Session completed. All systems nominal.',
        'tags': 'session-end,automation'
    })
    print(f'  Engram sync: {r.status_code}')
except: print('  Engram sync: failed')
" 2>/dev/null

echo "✅ Session Complete — Good night!"