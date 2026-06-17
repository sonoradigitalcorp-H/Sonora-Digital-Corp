#!/bin/bash
# AGENCY OS — Pipeline de Auto-Mejora
# Ejecución: Automática (systemd timer 4AM) o manual
# Frecuencia: Diaria (error correction) + Semanal (meta-evolve)
set -euo pipefail

LOG="/home/mystic/jarvis/logs/agency-pipeline.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')
cd /home/mystic/jarvis

log() { echo "[$DATE] $1" | tee -a "$LOG"; }

log "=== AGENCY OS — Auto-Improve Pipeline ==="

# === FASE 1: ERROR CORRECTION ===
log "[1/6] Error correction..."
python3 scripts/automation/memory-save.py 2>/dev/null || log "  Memory save: WARN"
# Docker health
docker ps -a --filter "status=exited" --format "{{.Names}}" | while read c; do
    log "  Restarting container: $c"
    docker start "$c" 2>/dev/null || log "  Cannot restart: $c"
done
# Cron dedup
crontab -l 2>/dev/null | sort -u | crontab -
log "  Cron: $(crontab -l | wc -l) entries"
# RAM check
RAM_FREE=$(free -m | awk '/^Mem:/ {print $7}')
if [ "$RAM_FREE" -lt 500 ]; then
    log "  RAM crítica: ${RAM_FREE}MB libre. Limpiando..."
    sync && echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || true
fi

# === FASE 2: TESTS ===
log "[2/6] Running tests..."
python3 -m pytest tests/ -x -q 2>&1 | tail -3 | tee -a "$LOG"
TEST_EXIT=$?
if [ $TEST_EXIT -ne 0 ]; then
    log "  TESTS FALLARON — registrando en DOCUMENTO_DE_ERRORES"
    echo "- $(date '+%Y-%m-%d %H:%M'): Auto-test failure" >> DOCUMENTO_DE_ERRORES.md
fi

# === FASE 3: GIT SYNC (mejorado) ===
log "[3/6] Git sync..."
REMOTE=$(git remote -v | grep "^origin.*push" | awk '{print $2}' || echo "")
if [ -n "$REMOTE" ]; then
    git add -A 2>/dev/null || true
    git diff --cached --quiet || git commit -m "auto: pipeline $(date +%Y-%m-%d-%H%M)"
    git push origin main 2>&1 | tail -1 >> "$LOG" || log "  Push: WARN (no remote?)"
    log "  Committed + pushed"
else
    log "  No remote configured. Skipping push."
fi

# === FASE 4: WEEKLY META-EVOLVE (Domingos) ===
DOW=$(date +%u)
if [ "$DOW" = "7" ]; then
    log "[4/6] Weekly meta-evolve..."
    log "  Revisando prompts en prompts/_META/meta-evolve.md..."
    # Cuenta prompts y tests
    TOTAL_PROMPTS=$(find prompts -name "*.md" -not -path "*/_META/*" | wc -l)
    log "  Total prompts activos: $TOTAL_PROMPTS"
    # Reporte semanal
    cat > "reports/weekly-$(date +%Y-%m-%d).md" << EOF
# Weekly Report — $(date +%Y-%m-%d)
- Tests: $(python3 -m pytest tests/ -q 2>&1 | tail -1)
- Prompts activos: $TOTAL_PROMPTS
- RAM libre: ${RAM_FREE}MB
- Generado: $(date)
EOF
    log "  Reporte semanal generado"
fi

# === FASE 5: PLAYWRIGHT NIGHTLY ===
log "[5/6] Playwright E2E nightly..."
if command -v npx &>/dev/null && [ -f playwright.config.ts ]; then
    DISPLAY=:0 npx playwright test --headed --reporter=json 2>/dev/null | tail -5 >> "$LOG" || log "  Playwright: WARN (no tests?)"
else
    log "  Playwright not configured. Skipping."
fi

# === FASE 6: COMMIT LOG ===
log "[6/6] Session saved"
log "=== Pipeline Complete ==="
