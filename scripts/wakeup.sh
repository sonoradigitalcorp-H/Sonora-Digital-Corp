#!/bin/bash
# Wake-up call — abre JARVIS en HDMI y saluda
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
LOG="$BASE_DIR/logs/wakeup.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
mkdir -p "$BASE_DIR/logs"

log() { echo "[$TIMESTAMP] $*" >> "$LOG"; echo "[$TIMESTAMP] $*"; }

log "=== Wake-up call ==="

# Kill any existing Chrome sessions
pkill -f "google-chrome.*kiosk" 2>/dev/null || true
sleep 1

# Open all 5 systems in Chrome kiosk on HDMI
export DISPLAY=:0
google-chrome --new-window --kiosk \
    "http://localhost:5174/static/agency-control.html" \
    "http://localhost:5174/static/abe-system.html" \
    "http://localhost:5174/static/zamora-system.html" \
    "http://localhost:5174/static/sdc-portal.html" \
    "http://localhost:5174/static/mysticverse-hub.html" &
log "✅ Opened 5 systems on HDMI at 9 AM wake-up"
