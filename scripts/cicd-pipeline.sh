#!/bin/bash
# CI/CD Pipeline — test, commit, push cada 6h
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
LOG="$BASE_DIR/logs/cicd.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
mkdir -p "$BASE_DIR/logs"

TELEGRAM_TOKEN=$(grep '^ABE_TELEGRAM_TOKEN=' "$BASE_DIR/.env" 2>/dev/null | cut -d= -f2)
TELEGRAM_CHAT=$(grep '^ABE_TELEGRAM_CHAT=' "$BASE_DIR/.env" 2>/dev/null | cut -d= -f2)

log() { echo "[$TIMESTAMP] $*" >> "$LOG"; echo "[$TIMESTAMP] $*"; }

send_telegram() {
    local msg="$1"
    if [ -n "$TELEGRAM_TOKEN" ] && [ -n "$TELEGRAM_CHAT" ]; then
        curl -sf -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
            -d "chat_id=${TELEGRAM_CHAT}" \
            -d "text=${msg}" \
            -d "parse_mode=HTML" > /dev/null 2>&1 || log "⚠️ Telegram send failed"
    fi
}

cd "$BASE_DIR" || { log "❌ Cannot cd to $BASE_DIR"; exit 1; }

log "=== CI/CD Pipeline ==="

# 1. Run tests (with 120s timeout to prevent hanging)
log "🔬 Running tests..."
# Disable pytest-asyncio plugin (v1.3.0 incompatible with pytest 9.0)
set +e
TEST_OUTPUT=$(timeout 120 python3 -m pytest tests/unit/ -q --tb=short \
    -p no:asyncio 2>&1)
TEST_EXIT=$?
set -e

if [ $TEST_EXIT -eq 0 ]; then
    log "✅ Tests PASSED"
    # Extract passed count
    PASSED=$(echo "$TEST_OUTPUT" | grep -oP '\d+ passed' | tail -1 | grep -oP '\d+')
    FAILED=0

    # 2. Git commit & push
    log "🔄 Committing and pushing..."
    git add -A
    git commit -m "auto: cicd $(date +%Y-%m-%d_%H:%M)" 2>&1 || log "ℹ️ Nothing to commit"
    PUSH_OUTPUT=$(git push origin main 2>&1) || log "⚠️ Push issue: $PUSH_OUTPUT"
else
    log "❌ Tests FAILED (exit $TEST_EXIT)"
    FAILED=$(echo "$TEST_OUTPUT" | grep -oP '\d+ failed' | tail -1 | grep -oP '\d+')
    PASSED=$(echo "$TEST_OUTPUT" | grep -oP '\d+ passed' | tail -1 | grep -oP '\d+')
    [ -z "$FAILED" ] && FAILED=1
    [ -z "$PASSED" ] && PASSED=0

    # 3. Log failure & send alert
    FAILURE_SUMMARY=$(echo "$TEST_OUTPUT" | tail -20)
    log "❌ Failure summary:"
    echo "$FAILURE_SUMMARY" >> "$LOG"
    send_telegram "🚨 <b>CI/CD FAILED</b> — ${FAILED} test(s) failed
<b>Time:</b> ${TIMESTAMP}
<code>$(echo "$FAILURE_SUMMARY" | head -10 | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g')</code>"
fi

# 5. Status message
LAST_COMMIT=$(git log -1 --format="%h %s" 2>/dev/null || echo "N/A")
RAM_TOTAL=$(free -m | awk '/Mem:/ {print $2}')
RAM_USED=$(free -m | awk '/Mem:/ {print $3}')
RAM_PCT=$(free -m | awk '/Mem:/ {printf "%.0f", $3/$2 * 100}')
DAEMON_STATUS=$(systemctl --user is-active abe-daemon.service 2>/dev/null || echo "unknown")

# 6. Check 5 HTML files
MISSING_FILES=()
for f in agency-control.html abe-system.html zamora-system.html sdc-portal.html mysticverse-hub.html; do
    if [ ! -f "$BASE_DIR/webui/static/$f" ]; then
        MISSING_FILES+=("$f")
    fi
done

STATUS_MSG="<b>🤖 CI/CD Status — ${TIMESTAMP}</b>
✅ Tests: ${PASSED:-0} passed, ${FAILED:-0} failed
🔑 Last commit: ${LAST_COMMIT}
💾 RAM: ${RAM_USED}MB/${RAM_TOTAL}MB (${RAM_PCT}%)
⚙️ Daemon: ${DAEMON_STATUS}
📄 Files OK: $([ ${#MISSING_FILES[@]} -eq 0 ] && echo '✅ 5/5' || echo "❌ Missing: ${MISSING_FILES[*]}")"

send_telegram "$STATUS_MSG"
log "✅ CI/CD complete — Tests: ${PASSED:-0} passed, ${FAILED:-0} failed | RAM: ${RAM_PCT}% | Daemon: ${DAEMON_STATUS}"
