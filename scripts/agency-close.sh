#!/bin/bash
# AGENCY OS — Session Close Pipeline
# Ejecuta: Al final de cada sesión de trabajo
# Automatiza: close-loop + git + memory + report
set -euo pipefail

cd /home/mystic/jarvis
SESSION_DATE=$(date '+%Y-%m-%d')
LOG="logs/session-close-$SESSION_DATE.log"

echo "=== AGENCY OS — Session Close ===" | tee "$LOG"
echo "Fecha: $(date)" | tee -a "$LOG"

# 1. Últimos tests
echo "[1/5] Running final tests..." | tee -a "$LOG"
python3 -m pytest tests/ -q 2>&1 | tee -a "$LOG"
TEST_EXIT=$?

# 2. Git status + commit
echo "[2/5] Git commit..." | tee -a "$LOG"
git add -A 2>/dev/null || true
STAGED=$(git diff --cached --stat 2>/dev/null | tail -1 || echo "")
if [ -n "$STAGED" ]; then
    git commit -m "v$(date +%Y%m%d%H%M): session close — $(date +%Y-%m-%d)"
    echo "   Committed: $STAGED"
else
    echo "   No changes to commit"
fi

# 3. Push
echo "[3/5] Pushing to GitHub..." | tee -a "$LOG"
git push origin main 2>&1 | tail -1 >> "$LOG" || echo "   WARN: push failed (no remote?)"

# 4. Memory log
echo "[4/5] Saving session memory..." | tee -a "$LOG"
cat >> "memory/session-log-$SESSION_DATE.md" << EOF
# Session: $SESSION_DATE
- Tests: $(python3 -m pytest tests/ -q 2>&1 | tail -1)
- RAM: $(free -h | awk '/^Mem:/ {print $3 " used / " $2 " total"}')
- Swap: $(free -h | awk '/^Swap:/ {print $3 " used / " $2 " total"}')
- Close: $(date '+%H:%M')
---
EOF

# 5. Limpieza
echo "[5/5] Cleanup..." | tee -a "$LOG"
docker system prune -f 2>/dev/null || true

echo "=== Session Close Complete ===" | tee -a "$LOG"
echo "Abreviatura: ./scripts/agency-close.sh"
