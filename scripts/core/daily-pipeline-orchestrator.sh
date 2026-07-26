#!/bin/bash
# SDC Daily Pipeline Orchestrator
# Runs scheduled tasks via systemd timers
set -e
MCP="http://127.0.0.1:8180/mcp/execute"
DATE=$(date +%Y-%m-%d)
LOG="/home/ubuntu/sonora-digital-corp/core/state/logs/pipeline-$(date +%H).log"
mkdir -p "$(dirname "$LOG")"

log() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG"; }
mcp() {
  local result
  result=$(curl -s "$MCP" -X POST -H "Content-Type: application/json" -d "$1" --max-time 120)
  echo "$result" >> "$LOG"
  echo "$result"
}

HOUR=$(date +%H)
case "$HOUR" in
  06)
    log "=== PIPELINE: Daily Content ==="
    log "Ejecutando daily-content-pipeline.sh..."
    bash /home/ubuntu/sonora-digital-corp/core/scripts/daily-content-pipeline.sh || true
    ;;
  08)
    log "=== PIPELINE: Analytics Report ==="
    mcp '{"tool":"hasura_query","args":{"query":"{ artists { name streams revenue } }"}}'
    mcp '{"tool":"engram_search","args":{"tenant_id":"abe-music","query":"pipeline content"}}'
    log "Analytics complete"
    ;;
  10)
    log "=== PIPELINE: Social Trends ==="
    mcp '{"tool":"firecrawl_scrape","args":{"url":"https://trends.google.com/trending?geo=MX"}}' || true
    log "Social trends check complete"
    ;;
  12)
    log "=== PIPELINE: Payment Reconciliation ==="
    mcp '{"tool":"hasura_query","args":{"query":"{ transactions(where: {status: {_eq: pending}}) { id amount provider } }"}}'
    log "Payment reconciliation complete"
    ;;
  18)
    log "=== PIPELINE: Daily Summary ==="
    mcp '{"tool":"hasura_query","args":{"query":"{ transactions_aggregate { aggregate { count sum { amount } } } }"}}'
    log "Daily summary complete"
    ;;
esac
log "Pipeline hora $HOUR done"
