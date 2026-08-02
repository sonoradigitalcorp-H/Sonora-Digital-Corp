#!/bin/bash
# Auto-healing watchdog — verifica servicios y los reinicia si están caídos
# Se ejecuta vía cron cada 5 minutos

LOG="/var/log/sdc/auto-heal.log"
mkdir -p /var/log/sdc

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG"; }

check_systemd() {
    local svc=$1
    if ! systemctl is-active --quiet "$svc" 2>/dev/null; then
        log "⚠️  $svc caído. Reiniciando..."
        sudo systemctl restart "$svc" 2>>"$LOG"
        sleep 3
        if systemctl is-active --quiet "$svc" 2>/dev/null; then
            log "✅ $svc reiniciado correctamente"
        else
            log "❌ $svc no pudo reiniciarse"
        fi
    fi
}

check_http() {
    local name=$1 url=$2
    if ! curl -s --max-time 5 "$url" > /dev/null 2>&1; then
        log "⚠️  $name no responde en $url"
        return 1
    fi
    return 0
}

check_docker() {
    local name=$1
    if ! docker ps --format "{{.Names}}" | grep -q "^${name}$" 2>/dev/null; then
        log "⚠️  Docker $name caído. Reiniciando..."
        docker start "$name" 2>>"$LOG"
        sleep 3
        if docker ps --format "{{.Names}}" | grep -q "^${name}$" 2>/dev/null; then
            log "✅ Docker $name reiniciado"
        else
            log "❌ Docker $name no pudo reiniciarse"
        fi
    fi
}

# Verificar servicios systemd
check_systemd sdc-aztrotech-bot
check_systemd sdc-aztrotech-notif
check_systemd sdc-aztrotech-tts

# Verificar Docker containers
check_docker infra-postgres-1
check_docker infra-qdrant-1
check_docker infra-redis-1
check_docker infra-n8n-1

# Verificar HTTP endpoints
check_http "TTS" "http://localhost:8765/health" || true
check_http "Qdrant" "http://localhost:6333/collections" || true
check_http "n8n" "http://localhost:5678/healthz" || true

# Verificar Postgres
if ! PGPASSWORD=sdc_local_dev psql -h localhost -U sdc -d sdc -c "SELECT 1" > /dev/null 2>&1; then
    log "⚠️  Postgres no responde. Reiniciando Docker..."
    docker restart infra-postgres-1 2>>"$LOG"
fi

# Verificar Redis
if ! redis-cli ping > /dev/null 2>&1; then
    log "⚠️  Redis no responde. Reiniciando Docker..."
    docker restart infra-redis-1 2>>"$LOG"
fi

log "✅ Health check completado"
