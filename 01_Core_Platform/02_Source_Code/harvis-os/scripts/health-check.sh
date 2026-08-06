#!/bin/bash
# Harvis OS - Health Check & Auto-Restart
# Ejecutar cada 5 minutos desde cron: */5 * * * * /path/to/health-check.sh

HARVIS_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_FILE="/tmp/harvis_health.log"
HEALTH_URL="http://localhost:8000/health"

check_health() {
    local response
    response=$(curl -sf -o /dev/null -w "%{http_code}" "$HEALTH_URL" 2>/dev/null)
    echo "$response"
}

send_alert() {
    local msg="$1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠ $msg" >> "$LOG_FILE"
    # Intentar notificar por Telegram si el bot está configurado
    if command -v curl &>/dev/null; then
        BOT_TOKEN=$(grep TELEGRAM_BOT_TOKEN /home/mystic/.hermes/.env 2>/dev/null | cut -d= -f2-)
        CHAT_ID=$(grep TELEGRAM_CHAT_ID /home/mystic/.hermes/.env 2>/dev/null | cut -d= -f2-)
        if [ -n "$BOT_TOKEN" ] && [ -n "$CHAT_ID" ]; then
            curl -sf "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
                -d "chat_id=$CHAT_ID" \
                -d "text=⚠️ Harvis OS: $msg" > /dev/null 2>&1 || true
        fi
    fi
}

case $(check_health) in
    200)
        # Todo bien
        exit 0
        ;;
    "")
        # No responde — reiniciar
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✗ API no responde, reiniciando..." >> "$LOG_FILE"
        send_alert "API caída, reiniciando..."
        bash "$HARVIS_DIR/scripts/start-auto.sh" >> "$LOG_FILE" 2>&1
        sleep 3
        if [ "$(check_health)" = "200" ]; then
            send_alert "API reiniciada exitosamente"
        else
            send_alert "FALLO crítico: no se pudo reiniciar la API"
        fi
        ;;
    *)
        # Otro código HTTP — reportar
        local code
        code=$(check_health)
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠ Health check devolvió código $code" >> "$LOG_FILE"
        send_alert "Health check inesperado: código $code"
        ;;
esac

# Rotar log si es muy grande (>1MB)
if [ -f "$LOG_FILE" ] && [ "$(stat -c%s "$LOG_FILE" 2>/dev/null)" -gt 1048576 ]; then
    tail -100 "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE"
fi