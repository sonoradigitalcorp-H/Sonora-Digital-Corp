#!/bin/bash
# JARVIS — Self-Improvement Loop
# Se ejecuta automáticamente, analiza el código, y sugiere mejoras
# bash scripts/self-improve.sh
set -euo pipefail

cd /home/mystic/sonora-digital-corp
LOG="logs/self-improve.log"
mkdir -p logs

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }

log "=== JARVIS Self-Improvement ==="

# 1. Verificar tests
log "🔍 Tests..."
if python3 -m pytest tests/ -q --tb=no 2>&1 | tail -3; then
    log "✅ Tests: OK"
else
    log "❌ Tests: FAILED"
fi

# 2. Verificar servicios
for svc in jarvis-neo4j hermes_qdrant; do
    if docker ps --format '{{.Names}}' | grep -q "$svc"; then
        log "✅ $svc: running"
    else
        log "❌ $svc: down"
    fi
done

# 3. Verificar SDD specs
specs=$(find specs -name "spec.md" | wc -l)
tasks=$(find specs -name "tasks.md" | wc -l)
completed=$(grep -r "✅" specs/*/tasks.md 2>/dev/null | wc -l)
total=$(grep -c "\[.\]" specs/*/tasks.md 2>/dev/null || echo 0)
log "📊 SDD: $specs specs, $tasks task files, ~$completed items completed"

# 4. Verificar Web UI
if curl -sf http://localhost:5174/api/status > /dev/null 2>&1; then
    log "✅ Web UI: http://localhost:5174"
else
    log "❌ Web UI: down"
    log "   Iniciar: python3 webui/fastapp.py &"
fi

# 5. Git stats
if git status --porcelain 2>/dev/null | grep -q .; then
    dirty=$(git status --porcelain | wc -l)
    log "📝 Git: $dirty archivos sin commit"
else
    log "✅ Git: limpio"
fi

# 6. Resumen
log ""
log "=== Resumen ==="
log "Tests: $(python3 -m pytest tests/ -q --tb=no 2>&1 | tail -1)"
log "SDD: $specs specs activas"
log "Próximo: specs/005-three-panel-web-ui/tasks.md (implementar pending tasks)"

log ""
log "✅ Self-improvement check complete"
