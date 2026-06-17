#!/bin/bash
# Daily Autonomous Pipeline — Sonora Digital Corp
# Runs every morning: tests, healthcheck, ABE report, notifications
set -euo pipefail

cd /home/mystic/sonora-digital-corp
BASE_DIR="/home/mystic/sonora-digital-corp"
STATE_DIR="$BASE_DIR/state"
LOG_DIR="$STATE_DIR/logs"
mkdir -p "$LOG_DIR" "$STATE_DIR/backups"

LOG="$LOG_DIR/daily-pipeline.log"
PUSH="$BASE_DIR/scripts/push-to-gateway.sh"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }

log "============================================"
log "DAILY PIPELINE START"
log "============================================"

START_EPOCH=$(date +%s)
FAILURES=0
SUCCESSES=0

run() {
    local step="$1"; shift
    log "▶ $step..."
    if "$@" >> "$LOG" 2>&1; then
        log "  ✅ $step"
        SUCCESSES=$((SUCCESSES + 1))
    else
        log "  ❌ $step"
        FAILURES=$((FAILURES + 1))
    fi
}

# ── 1. Git sync ──────────────────────────────
run "Git fetch" git fetch origin
BEHIND=$(git rev-list HEAD..origin/main --count 2>/dev/null || echo 0)
if [ "$BEHIND" -gt 0 ]; then
    run "Git pull" git pull origin main
fi

# ── 2. Run unit tests ────────────────────────
run "Unit tests" python -m pytest tests/unit/ -q --tb=no
UNIT_RESULT=$?

# ── 3. Healthcheck ───────────────────────────
SERVICES_UP=0
SERVICES_DOWN=0
for svc in "http://localhost:5174/health" "http://localhost:8000/health" "http://localhost:18789/health"; do
    if curl -sf --max-time 5 "$svc" > /dev/null 2>&1; then
        SERVICES_UP=$((SERVICES_UP + 1))
    else
        SERVICES_DOWN=$((SERVICES_DOWN + 1))
    fi
done
log "  Services: $SERVICES_UP up, $SERVICES_DOWN down"
[ "$SERVICES_DOWN" -eq 0 ] && SUCCESSES=$((SUCCESSES + 1)) || FAILURES=$((FAILURES + 1))

# ── 4. Check disk ────────────────────────────
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
log "  Disk: ${DISK_USAGE}%"
if [ "$DISK_USAGE" -lt 90 ]; then
    SUCCESSES=$((SUCCESSES + 1))
else
    log "  ⚠️ Disk at ${DISK_USAGE}%"
    FAILURES=$((FAILURES + 1))
fi

# ── 5. ABE Music Dashboard check ─────────────
ABE_DATA=$(curl -sf http://localhost:5174/api/abe/dashboard/ceo 2>/dev/null || echo '{}')
STREAMS=$(echo "$ABE_DATA" | python3 -c "import sys,json; print(json.load(sys.stdin).get('total_streams','?'))" 2>/dev/null || echo "?")
REVENUE=$(echo "$ABE_DATA" | python3 -c "import sys,json; print(json.load(sys.stdin).get('total_revenue','?'))" 2>/dev/null || echo "?")
log "  ABE Music: streams=$STREAMS revenue=$REVENUE"
[ "$STREAMS" != "?" ] && SUCCESSES=$((SUCCESSES + 1)) || FAILURES=$((FAILURES + 1))

# ── 6. Engram sync ──────────────────────────
if [ -f "$STATE_DIR/engram.db" ]; then
    python3 -c "import sqlite3; conn=sqlite3.connect('$STATE_DIR/engram.db'); c=conn.cursor(); c.execute('SELECT COUNT(*) FROM memories'); count=c.fetchone()[0]; conn.close(); print(f'  Engram: {count} memories')" >> "$LOG"
    SUCCESSES=$((SUCCESSES + 1))
else
    log "  ⚠️ Engram DB not found"
    FAILURES=$((FAILURES + 1))
fi

# ── 7. Check for pending ideas ──────────────
PENDING_IDEAS=$(python3 -c "
import sqlite3
try:
    conn = sqlite3.connect('$STATE_DIR/engram.db')
    c = conn.cursor()
    c.execute(\"SELECT COUNT(*) FROM memories WHERE tag='idea:pending'\")
    print(c.fetchone()[0])
    conn.close()
except: print(0)
" 2>/dev/null || echo 0)
log "  Pending ideas: $PENDING_IDEAS"

# ── 8. Generate and push summary ─────────────
DURATION=$(( $(date +%s) - START_EPOCH ))
SUMMARY="🤖 SDC Daily Pipeline · $(date '+%d %b %Y')
✅ ${SUCCESSES} checks passed
❌ ${FAILURES} checks failed
⏱ ${DURATION}s
📊 Tests: $([ $UNIT_RESULT -eq 0 ] && echo 'PASS' || echo 'FAIL')
🔧 Services: ${SERVICES_UP} up, ${SERVICES_DOWN} down
💾 Disk: ${DISK_USAGE}%
🎵 ABE: ${STREAMS} streams, \$${REVENUE}
💡 Ideas pendientes: ${PENDING_IDEAS}"

log "$SUMMARY"

# Push to Telegram
if [ -f "$PUSH" ]; then
    bash "$PUSH" "$SUMMARY" >> "$LOG" 2>&1 || log "⚠️ Push failed"
fi

log "============================================"
log "DAILY PIPELINE DONE — ${SUCCESSES} ok, ${FAILURES} fail, ${DURATION}s"
log "============================================"

exit $FAILURES
