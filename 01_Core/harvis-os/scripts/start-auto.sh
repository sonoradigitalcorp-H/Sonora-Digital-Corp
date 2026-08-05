#!/bin/bash
# Harvis OS - Start Automático (no interactivo)
set -e

HARVIS_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_FILE="/tmp/harvis_start.log"
PID_FILE="/tmp/harvis_api.pid"

echo "[$(date '+%H:%M:%S')] 🚀 Harvis OS Auto-Start" | tee "$LOG_FILE"
echo "==============================" | tee -a "$LOG_FILE"

# 1. Verificar infraestructura Docker
echo "[1/4] Verificando infraestructura..." | tee -a "$LOG_FILE"
if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "redis"; then
    echo "  ✓ Redis listo" | tee -a "$LOG_FILE"
else
    echo "  ⚠ Redis no detectado, levantando..." | tee -a "$LOG_FILE"
    docker compose -f "$HARVIS_DIR/docker-compose.local.yml" up -d redis postgres 2>&1 | tee -a "$LOG_FILE"
    sleep 3
fi

# 2. Verificar API key
echo "[2/4] Verificando API key..." | tee -a "$LOG_FILE"
if [ -z "$OPENROUTER_API_KEY" ]; then
    export OPENROUTER_API_KEY=$(grep OPENROUTER_API_KEY /home/mystic/.hermes/.env 2>/dev/null | cut -d= -f2-)
fi
if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "  ✗ OPENROUTER_API_KEY no encontrada" | tee -a "$LOG_FILE"
    exit 1
fi
echo "  ✓ API key cargada" | tee -a "$LOG_FILE"

# 3. Matar proceso anterior si existe
echo "[3/4] Preparando puerto 8000..." | tee -a "$LOG_FILE"
if ss -tlnp | grep -q ':8000 '; then
    OLD_PID=$(ss -tlnp | grep ':8000 ' | grep -o 'pid=[0-9]*' | cut -d= -f2)
    echo "  ⚠ Puerto ocupado por PID $OLD_PID, matando..." | tee -a "$LOG_FILE"
    kill "$OLD_PID" 2>/dev/null || true
    sleep 2
fi
echo "  ✓ Puerto listo" | tee -a "$LOG_FILE"

# 4. Iniciar Harvis OS
echo "[4/4] Iniciando Harvis OS..." | tee -a "$LOG_FILE"
cd "$HARVIS_DIR"
nohup uvicorn src.core.main:app --host 0.0.0.0 --port 8000 > /tmp/harvis_api.log 2>&1 &
echo $! > "$PID_FILE"
sleep 4

# Verificar health
if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo "  ✓ Harvis OS corriendo en http://localhost:8000" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    echo "✅ Listo para trabajar" | tee -a "$LOG_FILE"
else
    echo "  ✗ Harvis OS no responde, revisar /tmp/harvis_api.log" | tee -a "$LOG_FILE"
    tail -10 /tmp/harvis_api.log 2>/dev/null | tee -a "$LOG_FILE"
    exit 1
fi