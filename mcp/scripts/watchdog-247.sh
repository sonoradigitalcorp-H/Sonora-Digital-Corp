#!/bin/bash
# WATCHDOG 24/7 — Sonora Digital Corp
# Corre cada 5 minutos. Verifica servicios y reinicia caídos.

MCP="http://127.0.0.1:18989"
SERVICES="n8n:5678 dashy:3004 uptime-kuma:3003 metabase:3002"
LOG="/tmp/watchdog.log"

for svc in $SERVICES; do
  NAME="${svc%%:*}"
  PORT="${svc#*:}"
  if ! docker ps --format '{{.Names}}' | grep -q "^$NAME$"; then
    echo "[$(date)] 🔴 $NAME caído" >> $LOG
    docker start $NAME 2>/dev/null && echo "[$(date)] ✅ $NAME reiniciado" >> $LOG
  fi
  if ! curl -so /dev/null --connect-timeout 3 http://127.0.0.1:$PORT 2>/dev/null; then
    echo "[$(date)] ⚠️ $NAME no responde en :$PORT" >> $LOG
  fi
done

DISK=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
MEM=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
[ "$DISK" -gt 85 ] && echo "[$(date)] ⚠️ Disco al ${DISK}%" >> $LOG
[ "$MEM" -gt 85 ] && echo "[$(date)] ⚠️ RAM al ${MEM}%" >> $LOG
