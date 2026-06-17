#!/bin/bash
# Deploy All — abre los 5 sistemas en Chrome kiosk en HDMI
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
LOG="$BASE_DIR/logs/deploy-all.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
mkdir -p "$BASE_DIR/logs"

log() { echo "[$TIMESTAMP] $*" >> "$LOG"; echo "[$TIMESTAMP] $*"; }

log "=== Deploy All ==="

# Kill any existing Chrome kiosk sessions
log "🔄 Killing existing Chrome kiosk sessions..."
pkill -f "google-chrome.*kiosk" 2>/dev/null || true
sleep 1

# Verify all 5 HTML files exist
SYSTEMS=(
    "agency-control.html"
    "abe-system.html"
    "zamora-system.html"
    "sdc-portal.html"
    "mysticverse-hub.html"
)
MISSING=0
for f in "${SYSTEMS[@]}"; do
    if [ -f "$BASE_DIR/webui/static/$f" ]; then
        log "✅ Found $f"
    else
        log "❌ MISSING: $f"
        MISSING=$((MISSING + 1))
    fi
done

if [ "$MISSING" -gt 0 ]; then
    log "⚠️ $MISSING system file(s) missing — proceeding anyway"
fi

# Open all 5 systems in Chrome kiosk on HDMI
export DISPLAY=:0
log "🚀 Opening all 5 systems in Chrome kiosk..."
google-chrome --new-window --kiosk \
    "http://localhost:5174/static/agency-control.html" \
    "http://localhost:5174/static/abe-system.html" \
    "http://localhost:5174/static/zamora-system.html" \
    "http://localhost:5174/static/sdc-portal.html" \
    "http://localhost:5174/static/mysticverse-hub.html" &
log "✅ All systems deployed on HDMI"

echo "[$TIMESTAMP] All 5 systems opened in Chrome kiosk on HDMI"
