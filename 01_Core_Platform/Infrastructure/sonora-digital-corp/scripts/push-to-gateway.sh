#!/bin/bash
# push-to-gateway — Envía mensaje a todos los gateways configurados
# Uso: push-to-gateway.sh "Mensaje a enviar"
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
LOG="$BASE_DIR/state/logs/gateway-push.log"
mkdir -p "$BASE_DIR/state/logs"

MESSAGE="${1:-$(cat /dev/stdin)}"
if [ -z "$MESSAGE" ]; then
    echo "Uso: push-to-gateway.sh \"Mensaje\""
    echo "  o: echo \"Mensaje\" | push-to-gateway.sh"
    exit 1
fi

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
log "=== Push to Gateways ==="

# Load .env
if [ -f "$BASE_DIR/.env" ]; then
    set -a; source "$BASE_DIR/.env"; set +a
fi

SUCCESS=0
FAIL=0

# Telegram
if [ -n "$ABE_TELEGRAM_TOKEN" ] && [ "$ABE_TELEGRAM_TOKEN" != "your_telegram_bot_token_here" ]; then
    CHAT_ID="${ABE_TELEGRAM_CHAT:-5738935134}"
    if curl -sf -X POST "https://api.telegram.org/bot${ABE_TELEGRAM_TOKEN}/sendMessage" \
        -d "chat_id=${CHAT_ID}" \
        -d "text=${MESSAGE}" \
        -d "parse_mode=Markdown" > /dev/null 2>&1; then
        log "✅ Telegram: sent"
        SUCCESS=$((SUCCESS + 1))
    else
        log "❌ Telegram: FAILED"
        FAIL=$((FAIL + 1))
    fi
else
    log "⚠️ Telegram: not configured"
fi

# Discord
if [ -n "$ABE_DISCORD_WEBHOOK" ]; then
    # Escape for JSON
    JSON_MSG=$(python3 -c "import json,sys; print(json.dumps(sys.argv[1]))" "$MESSAGE" 2>/dev/null || echo "$MESSAGE")
    if curl -sf -X POST "$ABE_DISCORD_WEBHOOK" \
        -H "Content-Type: application/json" \
        -d "{\"content\":$JSON_MSG,\"username\":\"ABE MUSIC Bot\"}" > /dev/null 2>&1; then
        log "✅ Discord: sent"
        SUCCESS=$((SUCCESS + 1))
    else
        log "❌ Discord: FAILED"
        FAIL=$((FAIL + 1))
    fi
else
    log "⚠️ Discord: not configured"
fi

# Save to outbox
echo "$MESSAGE" >> "$BASE_DIR/state/logs/gateway-outbox.log"

log "=== Result: $SUCCESS sent, $FAIL failed ==="
echo "✅ $SUCCESS gateway(s) delivered, $FAIL failed"
