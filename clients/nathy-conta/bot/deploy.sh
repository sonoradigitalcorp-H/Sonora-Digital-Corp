#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
BOT_DIR="$ROOT/bot"
WEB_DIR="$ROOT/web"

export NATHY_CONTA_TOKEN="${NATHY_CONTA_TOKEN:-8720440822:AAHAZcdNd1cZg1QI6GB48t27blhe2bkD-Hw}"

echo "==> Instalando dependencias..."
pip3 install -r "$ROOT/requirements.txt" -q

echo "==> Iniciando bot de Telegram..."
cd "$BOT_DIR"
python3 main.py &

echo "==> Sirviendo web en http://localhost:8080..."
cd "$WEB_DIR"
python3 -m http.server 8080 &

echo ""
echo "✅ Nathy Conta está funcionando:"
echo "   Bot:    https://t.me/Nathy_Conta_bot"
echo "   Web:    http://localhost:8080"
echo ""
echo "Presiona Ctrl+C para detener todo."
wait
