#!/usr/bin/env bash
# open-brain-monitor.sh
# Opens the JARVIS Command Center dashboard on the external monitor.
set -euo pipefail

DASHBOARD_URL="http://localhost:5174/api/brain/dashboard"

echo "  JARVIS Command Center"
echo "  ====================="
echo ""

# Check if the dashboard is reachable
if ! curl -sf "$DASHBOARD_URL" > /dev/null 2>&1; then
  echo "  JARVIS UI no disponible en $DASHBOARD_URL"
  echo "  Verifica: systemctl status jarvis-ui"
  exit 1
fi

# Open in default browser
xdg-open "$DASHBOARD_URL" 2>/dev/null || \
  google-chrome --new-window "$DASHBOARD_URL" > /dev/null 2>&1 || \
  firefox --new-window "$DASHBOARD_URL" > /dev/null 2>&1 || \
  echo "Abre manualmente: $DASHBOARD_URL"

echo ""
echo "  Abierto en el navegador."
echo ""
echo "  Para verlo en el monitor externo:"
echo "    1. Arrastra la ventana al monitor HDMI"
echo "    2. Presiona F11 para pantalla completa"
echo "    3. En Chrome: Menu > Fullscreen"
echo ""
echo "  Atajos:"
echo "    F11 / Cmd+Shift+F = Fullscreen"
echo "    Alt+F4 = Cerrar"
