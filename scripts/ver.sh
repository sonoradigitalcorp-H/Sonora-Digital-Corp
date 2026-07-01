#!/bin/bash
# Te dice como abrir algo del VPS en tu laptop
# Uso: bash scripts/ver.sh presentacion
#       bash scripts/ver.sh abe
#       bash scripts/ver.sh webui

MACHINE_JSON="$(dirname "$0")/../config/machines.json"

case "${1:-presentacion}" in
  presentacion|evo)
    PORT=8080
    URL="http://localhost:8080/"
    ;;
  abe|abe-service)
    PORT=5180
    URL="http://localhost:5180/pwa/"
    ;;
  webui|jarvis)
    PORT=5174
    URL="http://localhost:5174/"
    ;;
  *)
    PORT="${1}"
    URL="http://localhost:${1}/"
    ;;
esac

echo ""
echo "════════════════════════════════════════"
echo "  Para ver en tu laptop (Linux):"
echo "════════════════════════════════════════"
echo ""
echo "  PASO 1 — Conectate con forwarding:"
echo "    ssh -L ${PORT}:localhost:${PORT} ubuntu@149.56.46.173"
echo ""
echo "  PASO 2 — Abre en tu browser:"
echo "    ${URL}"
echo ""
echo "  O usa SSH config permanente:"
echo "    Host sdc-prod"
echo "      HostName 149.56.46.173"
echo "      User ubuntu"
echo "      LocalForward ${PORT} localhost:${PORT}"
echo ""
echo "    Luego solo: ssh sdc-prod"
echo ""
echo "  Alternativa (sin forwarding):"
echo "    http://149.56.46.173:${PORT}/"
echo "════════════════════════════════════════"
echo ""
