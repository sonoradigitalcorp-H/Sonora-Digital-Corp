#!/bin/bash
# Container Health Monitor — Detect→Diagnose→Recover→Retest→Document→Learn
# Runs every 15 min via cron: */15 * * * * /home/ubuntu/sdc/scripts/health-monitor.sh

set -euo pipefail

BASE_DIR="/home/ubuntu/sdc"
LOG="$BASE_DIR/state/logs/health-monitor.log"
EVENTS="$BASE_DIR/state/logs/events.jsonl"
mkdir -p "$(dirname "$LOG")"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
emit_event() {
  local event="$1" detail="$2"
  echo "{\"event\":\"${event}\",\"producer\":\"health-monitor\",\"timestamp\":\"$(date -u '+%Y-%m-%dT%H:%M:%SZ')\",\"payload\":{\"detail\":\"${detail}\"}}" >> "$EVENTS"
}

# ─── DETECT: Find unhealthy containers ───
UNHEALTHY=$(docker ps --format "{{.Names}}\t{{.Status}}" | grep -i unhealthy || true)
if [ -z "$UNHEALTHY" ]; then
  log "✅ All containers healthy"
  exit 0
fi

log "⚠️ Unhealthy containers detected:"
echo "$UNHEALTHY" | while IFS=$'\t' read -r name status; do
  log "  ❌ $name — $status"
done

emit_event "unhealthy_containers_detected" "$(echo "$UNHEALTHY" | wc -l) unhealthy"

# ─── DIAGNOSE + RECOVER ───
echo "$UNHEALTHY" | while IFS=$'\t' read -r name status; do
  log "🔧 Attempting recovery for $name..."
  docker restart "$name" 2>&1 | log
  sleep 10

  # ─── RETEST ───
  NEW_STATUS=$(docker ps --format "{{.Names}}\t{{.Status}}" | grep "^$name" | grep -i healthy || true)
  if [ -n "$NEW_STATUS" ]; then
    log "  ✅ $name recovered successfully"
    emit_event "container_recovered" "$name"
  else
    log "  ❌ $name still unhealthy after restart"
    emit_event "container_recovery_failed" "$name"
  fi
done

# ─── DOCUMENT ───
HEALTH_LOG="$BASE_DIR/state/logs/audit/health-$(date '+%Y%m%d-%H%M%S').log"
{
  echo "=== Health Monitor Report ==="
  echo "Timestamp: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  echo "Unhealthy found:"
  echo "$UNHEALTHY"
  echo "=== Post-recovery status ==="
  docker ps --format "table {{.Names}}\t{{.Status}}"
} > "$HEALTH_LOG"
log "📝 Report saved: $HEALTH_LOG"
