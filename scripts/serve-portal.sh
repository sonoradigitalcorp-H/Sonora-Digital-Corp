#!/usr/bin/env bash
# serve-portal.sh — Sirve el portal Grimoire y abre en navegador
set -euo pipefail

PORT="${1:-8080}"
DIR="$(dirname "$0")/../portal"

echo "✦ Mystic Grimoire — Portal SDC"
echo "  Server: http://localhost:$PORT"
echo "  Ctrl+C para detener"

python3 -m http.server "$PORT" --directory "$DIR" &
PID=$!
sleep 0.5

# Intentar abrir navegador
xdg-open "http://localhost:$PORT" 2>/dev/null || true
google-chrome "http://localhost:$PORT" 2>/dev/null || true
firefox "http://localhost:$PORT" 2>/dev/null || true

# Regenerar system.json antes de servir (opcional)
# python3 "$(dirname "$0")/generate-system-json.py"

wait $PID
