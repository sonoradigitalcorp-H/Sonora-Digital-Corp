#!/bin/bash
# gateway-healthcheck — Verifica estado de todos los gateways de comunicación
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
source "$BASE_DIR/.env" 2>/dev/null || true

echo "🔌 GATEWAY HEALTHCHECK"
echo "====================="

# Web (always active)
if curl -sf -o /dev/null http://localhost:5174/static/dashboard-abe.html; then
    echo "✅  Web Dashboard:       UP  → /static/dashboard-abe.html"
else
    echo "❌  Web Dashboard:       DOWN"
fi

if curl -sf -o /dev/null http://localhost:5174/static/abe-reporte-ejecutivo.html; then
    echo "✅  Web Report:          UP  → /static/abe-reporte-ejecutivo.html"
else
    echo "❌  Web Report:          DOWN"
fi

# API
if curl -sf http://localhost:5174/api/abe/dashboard/ceo > /dev/null 2>&1; then
    echo "✅  ABE API:             UP  → /api/abe/dashboard/ceo"
else
    echo "❌  ABE API:             DOWN"
fi

# Telegram
TELEGRAM_TOKEN=$(grep '^ABE_TELEGRAM_TOKEN=' "$BASE_DIR/.env" 2>/dev/null | cut -d= -f2)
if [ -n "$TELEGRAM_TOKEN" ] && [ "$TELEGRAM_TOKEN" != "your_telegram_bot_token_here" ]; then
    if curl -sf "https://api.telegram.org/bot${TELEGRAM_TOKEN}/getMe" > /dev/null 2>&1; then
        BOT_NAME=$(curl -sf "https://api.telegram.org/bot${TELEGRAM_TOKEN}/getMe" 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin)['result']['username'])" 2>/dev/null || echo "active")
        echo "✅  Telegram:            UP  → @${BOT_NAME}"
    else
        echo "❌  Telegram:            DOWN (token 401)"
        echo "     → Solución: BotFather → /regeneratetoken"
    fi
else
    echo "⚠️  Telegram:            NOT CONFIGURED"
fi

# Discord
DISCORD_WEBHOOK=$(grep '^ABE_DISCORD_WEBHOOK=' "$BASE_DIR/.env" 2>/dev/null | cut -d= -f2)
if [ -n "$DISCORD_WEBHOOK" ]; then
    echo "✅  Discord:             CONFIGURED"
else
    echo "⚠️  Discord:             NOT CONFIGURED"
fi

echo ""
echo "📋 Available commands:"
echo "  scripts/abe-report-push.sh      — Generate + push report to all gateways"
echo "  scripts/push-to-gateway.sh      — Push message to all gateways"
echo "  scripts/abe-delivery-gate.sh    — Verify delivery readiness"
echo "  scripts/abe-telegram-bot.py     — Start Telegram bot (needs token)"
echo "  scripts/behavior-analyzer.py    — Self-analysis & automation suggestions"
