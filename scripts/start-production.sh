#!/usr/bin/env bash
# start-production.sh — Lanza Kernel + Experience Layer + Event Listeners
# Uso:
#   ./scripts/start-production.sh              # start both
#   ./scripts/start-production.sh --kernel-only # only kernel daemon
#   ./scripts/start-production.sh --web-only    # only experience layer
#   ./scripts/start-production.sh --stop        # stop all
#   ./scripts/start-production.sh --status      # check status
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

KERNEL_PORT="${KERNEL_PORT:-8001}"
WEB_PORT="${WEB_PORT:-5173}"
KERNEL_LOG="${KERNEL_LOG:-state/logs/kernel-web.log}"
WEB_LOG="${WEB_LOG:-state/logs/web.log}"
PID_DIR="${PID_DIR:-state/pids}"

mkdir -p "$PID_DIR" "$(dirname "$KERNEL_LOG")" "$(dirname "$WEB_LOG")"

KERNEL_PID="$PID_DIR/kernel.pid"
WEB_PID="$PID_DIR/web.pid"

info()  { echo -e "\033[0;36m[INFO]\033[0m  $*"; }
ok()    { echo -e "\033[0;32m[OK]\033[0m    $*"; }
err()   { echo -e "\033[0;31m[ERR]\033[0m   $*"; }

case "${1:-}" in
  --stop)
    info "Stopping all services..."
    if systemctl is-active --quiet kernel.service 2>/dev/null; then
      sudo systemctl stop kernel.service && ok "Kernel stopped (systemd)" || err "Kernel stop failed"
    elif [ -f "$KERNEL_PID" ]; then
      kill "$(cat "$KERNEL_PID")" 2>/dev/null && ok "Kernel stopped" || err "Kernel not running"
      rm -f "$KERNEL_PID"
    fi
    if [ -f "$WEB_PID" ]; then
      kill "$(cat "$WEB_PID")" 2>/dev/null && ok "Experience Layer stopped" || err "Experience Layer not running"
      rm -f "$WEB_PID"
    fi
    exit 0
    ;;

  --status)
    echo "Service    PID     Status"
    echo "---------  ------  --------"
    if [ -f "$KERNEL_PID" ] && kill -0 "$(cat "$KERNEL_PID")" 2>/dev/null; then
      echo "Kernel     $(cat "$KERNEL_PID")  Running (:$KERNEL_PORT)"
    else
      echo "Kernel     -       Stopped"
    fi
    if [ -f "$WEB_PID" ] && kill -0 "$(cat "$WEB_PID")" 2>/dev/null; then
      echo "Web        $(cat "$WEB_PID")  Running (:$WEB_PORT)"
    else
      echo "Web        -       Stopped"
    fi
    exit 0
    ;;

  --kernel-only)
    START_KERNEL=true
    START_WEB=false
    ;;
  --web-only)
    START_KERNEL=false
    START_WEB=true
    ;;
  *)
    START_KERNEL=true
    START_WEB=true
    ;;
esac

# ─── Kernel Daemon ────────────────────────────────────────────────────────────
if [ "$START_KERNEL" = true ]; then
  info "Starting Kernel daemon on 127.0.0.1:$KERNEL_PORT..."
  touch "$KERNEL_LOG" 2>/dev/null || KERNEL_LOG="/tmp/kernel.log"
  PYTHONPATH="$ROOT" nohup python3 -m uvicorn kernel.app:app \
    --host 127.0.0.1 --port "$KERNEL_PORT" \
    --log-level info \
    >> "$KERNEL_LOG" 2>&1 &
  echo $! > "$KERNEL_PID"
  sleep 3
  if kill -0 "$(cat "$KERNEL_PID")" 2>/dev/null; then
    ok "Kernel running (PID $(cat "$KERNEL_PID"))"
  else
    err "Kernel failed to start — check $KERNEL_LOG"
    exit 1
  fi
fi

# ─── Experience Layer (SvelteKit) ────────────────────────────────────────────
if [ "$START_WEB" = true ]; then
  WEB_DIR="$ROOT/experience/web"
  if [ -d "$WEB_DIR" ]; then
    info "Starting Experience Layer on 0.0.0.0:$WEB_PORT..."
    cd "$WEB_DIR"
    nohup npx vite --host 0.0.0.0 --port "$WEB_PORT" \
      >> "$WEB_LOG" 2>&1 &
    echo $! > "$WEB_PID"
    cd "$ROOT"
    sleep 3
    if kill -0 "$(cat "$WEB_PID")" 2>/dev/null; then
      ok "Experience Layer running (PID $(cat "$WEB_PID"))"
    else
      err "Experience Layer failed to start — check $WEB_LOG"
    fi
  else
    warn "Experience Layer directory not found at $WEB_DIR — skipping"
  fi
fi

echo ""
echo "══════════════════════════════════════════"
echo "  Hermes Production Stack"
echo "══════════════════════════════════════════"
echo "  Kernel:   http://127.0.0.1:$KERNEL_PORT/health"
echo "  Web:      http://0.0.0.0:$WEB_PORT"
echo "  Events:   $ROOT/state/events/events.jsonl"
echo "  Logs:     $KERNEL_LOG / $WEB_LOG"
echo "  PIDs:     $PID_DIR/"
echo "══════════════════════════════════════════"
