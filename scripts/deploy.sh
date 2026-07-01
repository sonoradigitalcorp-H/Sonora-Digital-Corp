#!/bin/bash
# deploy — Genera presentacion de la sesion mas reciente y la despliega
# Uso: bash scripts/deploy.sh [session.json]

set -e

SONORA_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SESSION="${1:-$(ls -t "$SONORA_DIR/memory/learning"/session-*.json 2>/dev/null | head -1)}"

if [ ! -f "$SESSION" ]; then
  echo "❌ No session JSON found"
  echo "   Usage: bash scripts/deploy.sh [path/to/session.json]"
  exit 1
fi

echo "📄 Generating presentation from: $(basename "$SESSION")"
python3 "$SONORA_DIR/scripts/presentar.py" --session "$SESSION"

echo "🚀 Restarting dashboard server..."
systemctl --user restart evolucion-dashboard.service 2>/dev/null || \
  echo "   (dashboard not running as systemd, starting...)"

sleep 1
SESSION_DATE=$(basename "$SESSION" | sed 's/session-//;s/\.json//')
echo ""
echo "✅ Presentacion desplegada:"
echo "   http://$(curl -s ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}'):8080/presentacion-${SESSION_DATE}.html"
echo ""
