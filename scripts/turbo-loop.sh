#!/bin/bash
# TURBO-LOOP — Auto-optimización cada 10 minutos
# Corre como systemd timer. Mejora el sistema continuamente.
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$BASE_DIR/logs"
LOOP_LOG="$LOG_DIR/turbo-loop.log"
CONCLUSION_LOG="$LOG_DIR/turbo-conclusions.md"
mkdir -p "$LOG_DIR"

log() { 
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOOP_LOG"
}

CONCLUSION_HEADER="## Turbo-Loop $(date '+%Y-%m-%d %H:%M')\n\n| Hora | RAM | Containers | API | Bot | Fixes |\n|------|-----|-----------|-----|-----|-------|\n"

log "=== Turbo-Loop ==="

# 1. HEALTHCHECK RÁPIDO
RAM_FREE=$(free -m | awk '/Mem:/ {print $7}')
CONTAINERS=$(docker ps --format "{{.Names}}" 2>/dev/null | wc -l)
API_OK=$(curl -sf http://localhost:5174/api/status > /dev/null 2>&1 && echo "✅" || echo "❌")
BOT_OK=$(curl -sf "https://api.telegram.org/bot$(grep ABE_TELEGRAM_TOKEN "$BASE_DIR/.env" | cut -d= -f2)/getMe" > /dev/null 2>&1 && echo "✅" || echo "❌")

FIXES=0

# 2. AUTO-FIX: RAM crítica
if [ "$RAM_FREE" -lt 200 ]; then
    log "⚠️ RAM baja ($RAM_FREE MB) — matando procesos basura"
    kill -9 $(pgrep -f "warp-svc") 2>/dev/null || true
    kill -9 $(pgrep -f "openclaw") 2>/dev/null || true
    FIXES=$((FIXES + 1))
fi

# 3. AUTO-FIX: JARVIS caído
if [ "$API_OK" = "❌" ]; then
    log "⚠️ JARVIS caído — reiniciando contenedores"
    docker restart jarvis-neo4j hermes_api 2>/dev/null || true
    sleep 5
    FIXES=$((FIXES + 1))
fi

# 4. AUTO-FIX: Bot muerto
if [ "$BOT_OK" = "❌" ]; then
    log "❌ TELEGRAM BOT MUERTO — alertando"
    curl -s -X POST "https://api.telegram.org/bot$(grep ABE_TELEGRAM_TOKEN "$BASE_DIR/.env" | cut -d= -f2)/sendMessage" \
        -d "chat_id=$(grep ABE_TELEGRAM_CHAT "$BASE_DIR/.env" | cut -d= -f2)" \
        -d "text=⚠️ Turbo-Loop: Bot Telegram no responde. Regenera token en BotFather." > /dev/null 2>&1 || true
fi

# 5. REGISTRAR CONCLUSIÓN
LINE="| $(date '+%H:%M') | ${RAM_FREE}MB | ${CONTAINERS} | ${API_OK} | ${BOT_OK} | ${FIXES} |"

if [ ! -f "$CONCLUSION_LOG" ]; then
    echo -e "$CONCLUSION_HEADER" > "$CONCLUSION_LOG"
fi

# Mantener últimas 24 líneas (4 horas de ciclos)
{ head -2 "$CONCLUSION_LOG"; echo "$LINE"; tail -23 "$CONCLUSION_LOG" 2>/dev/null; } > /tmp/turbo-tmp.md 2>/dev/null
mv /tmp/turbo-tmp.md "$CONCLUSION_LOG" 2>/dev/null || echo "$LINE" >> "$CONCLUSION_LOG"

log "✅ Turbo-Loop complete: RAM=${RAM_FREE}MB Containers=${CONTAINERS} API=${API_OK} Bot=${BOT_OK} Fixes=${FIXES}"
