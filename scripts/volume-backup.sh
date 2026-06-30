#!/bin/bash
# Volume Backup — Docker volumes + config + git state
# Usage: ./volume-backup.sh [--s3] [--prune]
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="${BASE_DIR}/backups"
DATE=$(date '+%Y%m%d_%H%M%S')
LOG="${BACKUP_DIR}/volume-backup.log"
RESTIC_REPO="${BACKUP_DIR}/restic-repo"

mkdir -p "${BACKUP_DIR}"

log() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "${LOG}"; }

# ── 1. Backup Docker volumes ──
backup_volume() {
    local vol="$1"
    local out="${BACKUP_DIR}/${vol}-${DATE}.tar.gz"
    log "Backing up volume: ${vol}"
    if docker run --rm -v "${vol}:/source" alpine tar czf - -C /source . 2>/dev/null > "${out}"; then
        local size
        size=$(stat --format="%s" "${out}" 2>/dev/null || echo "0")
        log "  OK ${vol} (${size} bytes)"
    else
        log "  FAIL ${vol}"
    fi
}

log "=== Volume Backup ${DATE} ==="

# Get all sdc-* volumes
VOLUMES=$(docker volume ls --format "{{.Name}}" | grep "^sdc-\|^infra-" || true)
for vol in ${VOLUMES}; do
    backup_volume "${vol}"
done

# ── 2. Backup config + .env ──
log "Backing up config..."
tar czf "${BACKUP_DIR}/config-${DATE}.tar.gz" \
    -C "${BASE_DIR}" \
    .env opencode.json docker-compose.yml \
    --ignore-failed-read 2>/dev/null || true

# ── 3. Git log ──
cd "${BASE_DIR}"
git log --oneline -200 > "${BACKUP_DIR}/git-log-${DATE}.txt" 2>/dev/null || true

# ── 4. Integrity check ──
log "Integrity check..."
ERRORS=0
for f in "${BACKUP_DIR}"/*"${DATE}"*; do
    if [[ "${f}" == *.tar.gz ]]; then
        if tar tzf "${f}" >/dev/null 2>&1; then
            log "  OK $(basename "${f}")"
        else
            log "  CORRUPT $(basename "${f}")"
            ERRORS=$((ERRORS+1))
        fi
    fi
done

# ── 5. Init restic repo & add to it ──
if [ ! -d "${RESTIC_REPO}" ]; then
    restic init --repo "${RESTIC_REPO}" 2>/dev/null && log "Restic repo initialized"
fi

if [ -d "${RESTIC_REPO}" ]; then
    RESTIC_PASSWORD="${RESTIC_PASSWORD:-sdc-backup-2026}" restic backup \
        --repo "${RESTIC_REPO}" \
        --tag "sdc-${DATE}" \
        "${BACKUP_DIR}"/*"${DATE}"* 2>/dev/null && \
        log "Restic backup complete"
fi

# ── 6. Clean old backups (keep 14 days) ──
find "${BACKUP_DIR}" -maxdepth 1 -name "*.tar.gz" -mtime +14 -delete 2>/dev/null
log "Cleaned backups older than 14 days"

log "=== Complete (errors: ${ERRORS}) ==="
exit ${ERRORS}
