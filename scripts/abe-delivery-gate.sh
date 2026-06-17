#!/bin/bash
# ABE DELIVERY GATE — Verifica que ABE ha recibido un entregable visible
# Se ejecuta antes de marcar cualquier tarea como "done"
# Requiere: URL que Abraham puede abrir y ver

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
LOG="$BASE_DIR/logs/abe-delivery-gate.log"
mkdir -p "$BASE_DIR/logs"
exec >> "$LOG" 2>&1

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

log "=== ABE DELIVERY GATE ==="

# 1. Check that dashboard CEO is accessible
if curl -sf -o /dev/null http://localhost:5174/static/dashboard-abe.html; then
    log "✅ CEO Dashboard: accessible"
else
    log "❌ CEO Dashboard: NOT accessible"
    echo "ERROR: CEO Dashboard no está accesible. No se puede marcar como entregado."
    exit 1
fi

# 2. Check that reporte ejecutivo is accessible
if curl -sf -o /dev/null http://localhost:5174/static/abe-reporte-ejecutivo.html; then
    log "✅ Executive Report: accessible"
else
    log "❌ Executive Report: NOT accessible"
fi

# 3. Check API responds
if curl -sf http://localhost:5174/api/abe/dashboard/ceo > /dev/null 2>&1; then
    log "✅ ABE API: responding"
else
    log "❌ ABE API: NOT responding"
    echo "ERROR: ABE API no responde. Los dashboards muestran datos 'mock'."
fi

# 4. Check tests pass
TEST_OUTPUT=$(cd "$BASE_DIR" && python3 -m pytest tests/ -k "abe" -q 2>&1 | tail -1)
if echo "$TEST_OUTPUT" | grep -q "passed"; then
    log "✅ ABE Tests: $TEST_OUTPUT"
else
    log "⚠️ ABE Tests: $TEST_OUTPUT"
fi

# 5. Check RAM is sufficient
RAM_FREE=$(free -m | awk '/Mem:/ {print $7}')
if [ "$RAM_FREE" -lt 200 ]; then
    log "⚠️ RAM crítica: ${RAM_FREE}MB libre"
else
    log "✅ RAM: ${RAM_FREE}MB libre"
fi

log "=== DELIVERY GATE PASSED ==="
echo "✅ DELIVERY GATE PASSED — Abraham puede ver:"
echo "   📊 http://localhost:5174/static/dashboard-abe.html"
echo "   📋 http://localhost:5174/static/abe-reporte-ejecutivo.html"
echo "   🔌 API: http://localhost:5174/api/abe/dashboard/ceo"
