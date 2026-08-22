#!/usr/bin/env bash
# memory-guard.sh — Sonora Digital Corp (actualizado 2026-08-22, stack Hermes)
# Laptop 3.3GB RAM — evita freezes (lecciones sesión 2026-08-10)
# 1) Mata DUPLICADOS de gateway hermes (debe haber solo 1 por puerto lógico)
# 2) Alerta RAM < umbral (swap-thrash/OOM)
# 3) Mata MCP/dev accesorios si crítica (NO mata opencode/antigravity/hermes)
# Crons cada 5 min. LOG: /tmp/memory-guard.log

set -u
LOG=/tmp/memory-guard.log
NOW=$(date "+%F %T")
MEM=$(free -m | awk '/^Mem:/{print $7}')
TOTAL=$(free -m | awk '/^Mem:/{print $2}')
log() { echo "$NOW | $1" >> "$LOG"; }

# --- 1) Gateway Hermes: solo 1 proceso "gateway run" (stack actual, ya NO openclaw) ---
GWCOUNT=$(pgrep -fc "hermes_cli.main gateway run")
if [ "$GWCOUNT" -gt 1 ]; then
  # Matar los extra (el que tiene menor PID / más viejo se conserva)
  for pid in $(pgrep -f "hermes_cli.main gateway run" | sort -n | sed '1d'); do
    kill "$pid" 2>/dev/null && log "MATADO hermes gateway duplicado pid=$pid (n=$GWCOUNT)"
  done
fi

# --- 2) Umbral RAM crítica ---
CRIT=400
if [ "$MEM" -lt "$CRIT" ]; then
  log "ALERTA RAM disponible=${MEM}MB de ${TOTAL}MB (critico <${CRIT}MB)"
  # Solo accesorios MCP/dev — NUNCA opencode / antigravity / hermes gateway / wacli
  for pat in "mcp-server-fetch" "mcp-server-filesystem" "playwright-social" "pvporcupine" "mcp-server-github"; do
    for pid in $(pgrep -f "$pat" 2>/dev/null); do
      kill "$pid" 2>/dev/null && log "MATADO accesorio $pat pid=$pid (RAM critica)"
    done
  done
fi

# --- 3) Registro normal ---
[ "$MEM" -ge "$CRIT" ] && log "ok ram=${MEM}MB gw=${GWCOUNT}"
