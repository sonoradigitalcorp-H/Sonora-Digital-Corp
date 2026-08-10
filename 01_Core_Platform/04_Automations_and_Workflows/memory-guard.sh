#!/usr/bin/env bash
# memory-guard.sh — Sonora Digital Corp
# Evita freezes en laptop 3.3GB RAM (lecciones sesión 2026-08-10)
# 1) Mata procesos DUPLICADOS de openclaw gateway (crash-loop breaker spawns)
# 2) Alerta cuando RAM disponible < umbral (swap-thrash/OOM killer)
# 3) Mata procesos MCP/dev no esenciales si crítica
# Corre via cron cada 5 min. LOG: /tmp/memory-guard.log

set -u
LOG=/tmp/memory-guard.log
NOW=$(date "+%F %T")

MEM=$(free -m | awk '/^Mem:/{print $7}')          # MB disponibles
TOTAL=$(free -m | awk '/^Mem:/{print $2}')

log() { echo "$NOW | $1" >> "$LOG"; }

# --- 1) Duplicados de openclaw gateway: solo debe haber 1 PID escuchando en 18789 ---
GWPIDS=$(ss -tlnp 2>/dev/null | grep "18789" | grep -oP 'pid=\K[0-9]+' | sort -u)
GW=$(echo "$GWPIDS" | wc -l)
if [ "$GW" -gt 1 ]; then
  # Si systemd está sano, matar los extras
  if systemctl --user is-active openclaw-gateway >/dev/null 2>&1; then
    FIRST=""
    for pid in $GWPIDS; do
      if [ -z "$FIRST" ]; then FIRST=$pid; continue; fi
      kill "$pid" 2>/dev/null && log "MATADO openclaw duplicado pid=$pid (pids=$GW)"
    done
  fi
fi

# --- 2) Umbral de RAM crítica ---
CRIT=400   # MB disponibles < 400 = peligro swap/OOM
if [ "$MEM" -lt "$CRIT" ]; then
  log "ALERTA RAM disponible=${MEM}MB de ${TOTAL}MB (critico <${CRIT}MB)"
  # Matar procesos MCP/dev accesorios (NO matar opencode/antigravity/openclaw)
  for pat in "chrome-devtools-mcp" "mcp-server-filesystem"; do
    for pid in $(pgrep -f "$pat" 2>/dev/null); do
      kill "$pid" 2>/dev/null && log "MATADO accesorio $pat pid=$pid (RAM critica)"
    done
  done
fi

# --- 3) Registro normal (solo si no hay nada que hacer) ---
[ "$MEM" -ge "$CRIT" ] && log "ok ram=${MEM}MB gw=${GW}"