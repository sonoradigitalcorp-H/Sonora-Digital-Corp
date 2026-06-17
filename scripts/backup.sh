#!/bin/bash
# JARVIS Backup Script — v2.0
# Crea backups con timestamp, comprime en .tar.gz, verifica integridad

SOURCE_DIR="/home/mystic/sonora-digital-corp"
BACKUP_DIR="${SOURCE_DIR}/backups"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
BACKUP_PATH="${BACKUP_DIR}/${TIMESTAMP}"
LOG_FILE="${BACKUP_DIR}/backup-cron.log"
ERROR_LOG="${BACKUP_DIR}/errors.log"
TARBALL="${BACKUP_DIR}/sdc-${TIMESTAMP}.tar.gz"
KEEP_DAYS=7

mkdir -p "${BACKUP_PATH}"

{
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] ========================================"
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] SDC Backup — ${TIMESTAMP}"
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Target: ${BACKUP_PATH}"
  echo ""
} >> "${LOG_FILE}"

backup_dir() {
  local src="$1"
  if [ -d "$src" ]; then
    local dest="${BACKUP_PATH}/$(basename "$src")"
    cp -a "$src" "$dest" 2>> "${ERROR_LOG}"
    if [ $? -eq 0 ]; then
      echo "[$(date '+%Y-%m-%d %H:%M:%S')] OK  $(basename "$src")  ($(du -sh "$src" | cut -f1))" >> "${LOG_FILE}"
    else
      echo "[$(date '+%Y-%m-%d %H:%M:%S')] FAIL $(basename "$src")" >> "${LOG_FILE}"
    fi
  else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] MISSING $(basename "$src")" >> "${LOG_FILE}"
  fi
}

backup_file() {
  local src="$1"
  if [ -f "$src" ]; then
    cp -a "$src" "${BACKUP_PATH}/" 2>> "${ERROR_LOG}"
    if [ $? -eq 0 ]; then
      echo "[$(date '+%Y-%m-%d %H:%M:%S')] OK  $(basename "$src")" >> "${LOG_FILE}"
    else
      echo "[$(date '+%Y-%m-%d %H:%M:%S')] FAIL $(basename "$src")" >> "${LOG_FILE}"
    fi
  else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] MISSING $(basename "$src")" >> "${LOG_FILE}"
  fi
}

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Backing up directories..." >> "${LOG_FILE}"
backup_dir "${SOURCE_DIR}/sonora-enterprise-os"
backup_dir "${SOURCE_DIR}/apps"
backup_dir "${SOURCE_DIR}/config"
backup_dir "${SOURCE_DIR}/platforms"
backup_dir "${SOURCE_DIR}/products"
backup_dir "${SOURCE_DIR}/infra"
backup_dir "${SOURCE_DIR}/tests"
backup_dir "${SOURCE_DIR}/scripts"
backup_dir "${SOURCE_DIR}/state"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Backing up key files..." >> "${LOG_FILE}"
backup_file "${SOURCE_DIR}/opencode.json"
backup_file "${SOURCE_DIR}/apps/jarvis/main.py"
backup_file "${SOURCE_DIR}/infra/docker-compose.yml"
backup_file "${SOURCE_DIR}/CLAUDE.md"
backup_file "${SOURCE_DIR}/AGENTS.md"

# .opencode is a hidden dir, handle separately
if [ -d "${SOURCE_DIR}/.opencode" ]; then
  cp -a "${SOURCE_DIR}/.opencode" "${BACKUP_PATH}/" 2>> "${ERROR_LOG}"
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] OK  .opencode" >> "${LOG_FILE}"
else
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] MISSING .opencode" >> "${LOG_FILE}"
fi

# ── Git log (best-effort) ──
cd "${SOURCE_DIR}" 2>/dev/null
git log --oneline -100 > "${BACKUP_PATH}/git-log.txt" 2>/dev/null || true
git log --format="%H %ai %s" > "${BACKUP_PATH}/git-log-full.txt" 2>/dev/null || true

# ── Compress into tarball ──
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Creating tarball..." >> "${LOG_FILE}"
cd "${BACKUP_DIR}"
tar -czf "${TARBALL}" "${TIMESTAMP}" 2>> "${ERROR_LOG}"
if [ $? -eq 0 ]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Tarball created: ${TARBALL}" >> "${LOG_FILE}"
else
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Tarball FAILED" >> "${LOG_FILE}"
fi

# ── Verify ──
echo "[$(date '+%Y-%m-%d %H:%M:%S')] --- Verification ---" >> "${LOG_FILE}"
if [ -f "${TARBALL}" ]; then
  TAR_SIZE=$(stat --format="%s" "${TARBALL}")
  TAR_FILES=$(tar -tzf "${TARBALL}" 2>/dev/null | wc -l)
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Tarball size: ${TAR_SIZE} bytes, ${TAR_FILES} entries" >> "${LOG_FILE}"
else
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Tarball NOT FOUND" >> "${LOG_FILE}"
fi

# ── Clean old backups (keep last KEEP_DAYS days) ──
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Cleaning backups >${KEEP_DAYS} days old..." >> "${LOG_FILE}"
find "${BACKUP_DIR}" -maxdepth 1 -name "*.tar.gz" -type f -mtime +${KEEP_DAYS} -delete 2>> "${ERROR_LOG}"
find "${BACKUP_DIR}" -maxdepth 1 -type d -name "2*" -mtime +${KEEP_DAYS} -exec rm -rf {} \; 2>> "${ERROR_LOG}"

# ── Summary ──
echo "[$(date '+%Y-%m-%d %H:%M:%S')] ========================================" >> "${LOG_FILE}"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] BACKUP COMPLETE" >> "${LOG_FILE}"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Tarball: ${TARBALL}" >> "${LOG_FILE}"

if [ -f "${TARBALL}" ]; then
  ls -lh "${TARBALL}"
fi
echo "---"
if [ -s "${ERROR_LOG}" ]; then
  echo "[WARN] Some errors occurred. Check: ${ERROR_LOG}"
fi
