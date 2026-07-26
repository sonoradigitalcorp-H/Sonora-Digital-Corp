#!/bin/bash
# ─────────────────────────────────────────────────────
# auto-clean.sh — Sonora Digital Corp
# Limpieza automática semanal del VPS
# Previene que el disco se llene (mantiene <70% uso)
# ─────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_FILE="${REPO_DIR}/state/logs/autoclean.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

mkdir -p "${REPO_DIR}/state/logs"

log() {
  echo "[${TIMESTAMP}] $*" | tee -a "$LOG_FILE"
}

log "=== AutoClean SDC — INICIO ==="
log "Disco antes: $(df -h / | awk 'NR==2 {print $5" usado ("$3" de "$2")"}')"

# ─── 1. Docker: imágenes huerfanas (sin tag o sin usar >24h) ───
if command -v docker &>/dev/null; then
  log "[Docker] Limpiando imágenes colgantes..."
  docker image prune -af --filter "until=24h" 2>&1 | tee -a "$LOG_FILE"
  log "[Docker] Done."
else
  log "[Docker] No instalado. Skipping."
fi

# ─── 2. Backups: mantener solo los 5 más recientes ───
BACKUP_DIR="${REPO_DIR}/backups"
if [ -d "$BACKUP_DIR" ]; then
  TOTAL=$(ls -d "$BACKUP_DIR"/2* 2>/dev/null | wc -l)
  TO_DELETE=$((TOTAL - 5))
  if [ "$TO_DELETE" -gt 0 ]; then
    log "[Backups] $TOTAL encontrados. Borrando $TO_DELETE (keep=5)..."
    ls -dt "$BACKUP_DIR"/2* | tail -n "$TO_DELETE" | while read -r d; do
      rm -rf "$d"
      log "[Backups] Eliminado: $(basename "$d")"
    done
  else
    log "[Backups] $TOTAL encontrados. No requiere limpieza."
  fi
fi

# ─── 3. Logs del sistema (journal) ───
if command -v journalctl &>/dev/null; then
  log "[Journal] Comprimiendo a max 300MB..."
  sudo journalctl --vacuum-size=300M 2>&1 | tee -a "$LOG_FILE"
fi

# ─── 4. Cachés de paquetes ───
if command -v pip &>/dev/null; then
  log "[pip] Purgando caché..."
  pip cache purge 2>&1 | tee -a "$LOG_FILE"
fi

if command -v npm &>/dev/null; then
  log "[npm] Limpiando caché..."
  npm cache clean --force 2>&1 | tee -a "$LOG_FILE"
fi

if command -v pnpm &>/dev/null; then
  log "[pnpm] Podando store..."
  pnpm store prune 2>&1 | tee -a "$LOG_FILE"
fi

# ─── 5. /tmp: archivos sin acceso >7 días ───
log "[tmp] Eliminando archivos sin acceso >7 días..."
find /tmp -type f -atime +7 -delete 2>/dev/null || true

# ─── 6. Logs del proyecto >30 días ───
log "[State/Logs] Eliminando logs >30 días..."
find "${REPO_DIR}/state/logs" -name "*.log" -mtime +30 -delete 2>/dev/null || true

# ─── 7. Caché de HuggingFace si supera 1GB ───
HF_CACHE="$HOME/.cache/huggingface"
if [ -d "$HF_CACHE" ]; then
  HF_SIZE=$(du -sb "$HF_CACHE" 2>/dev/null | cut -f1)
  if [ "${HF_SIZE:-0}" -gt 1073741824 ]; then  # 1GB
    log "[HuggingFace] Caché >1GB. Limpiando modelos no usados..."
    rm -rf "$HF_CACHE"/models/* 2>/dev/null || true
    log "[HuggingFace] Done."
  fi
fi

# ─── 8. Reporte final ───
log "Disco después: $(df -h / | awk 'NR==2 {print $5" usado ("$3" de "$2")"}')"
DISK_PCT=$(df / | awk 'NR==2 {gsub(/%/,""); print $5}')
log "=== AutoClean SDC — FIN (uso: ${DISK_PCT}%) ==="
echo "" >> "$LOG_FILE"

# ─── 9. Alerta si disco sigue >80% ───
if [ "$DISK_PCT" -gt 80 ]; then
  MSG="⚠️ DISCO AL ${DISK_PCT}% después de AutoClean — requiere atención manual"
  echo "$MSG" | tee -a "$LOG_FILE"
  # Notificar por telegram si el bot está configurado
  if command -v curl &>/dev/null && [ -f "${REPO_DIR}/config/secrets/telegram.json" ]; then
    TOKEN=$(python3 -c "import json; print(json.load(open('${REPO_DIR}/config/secrets/telegram.json'))['bot_token'])" 2>/dev/null || echo "")
    CHAT_ID=$(python3 -c "import json; print(json.load(open('${REPO_DIR}/config/secrets/telegram.json'))['admin_chat_id'])" 2>/dev/null || echo "")
    if [ -n "$TOKEN" ] && [ -n "$CHAT_ID" ]; then
      curl -s -X POST "https://api.telegram.org/bot${TOKEN}/sendMessage" \
        -d "chat_id=${CHAT_ID}" \
        -d "text=${MSG}" &>/dev/null || true
    fi
  fi
fi
