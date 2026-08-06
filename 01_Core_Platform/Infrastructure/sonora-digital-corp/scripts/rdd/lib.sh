#!/bin/bash
# RDD common configuration — sourced by all rdd/*.sh scripts.
# Generic across the monorepo (defaults to repo root; override with RDD_ROOT / RDD_APP_DIR).

# Resolve repo root: this file is at <repo>/scripts/rdd/lib.sh
RDD_ROOT="${RDD_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"

# App dir under review (default: whole repo). Set RDD_APP_DIR=<path> to scope a subtree.
RDD_APP_DIR="${RDD_APP_DIR:-$RDD_ROOT}"

# Where freezes / receipts live (always under repo .rdd)
RDD_FREEZE_DIR="$RDD_ROOT/.rdd/freezes"

# Kill switch: disables gate only in documented emergency
RDD_KILLSWITCH="$RDD_ROOT/.rdd/killswitch.json"
RDD_GATE_ENABLED="${RDD_GATE_ENABLED:-1}"

rdd_gate_enabled() {
  if [ "$RDD_GATE_ENABLED" = "0" ]; then
    return 1
  fi
  if [ -f "$RDD_KILLSWITCH" ]; then
    local enabled
    enabled=$(python3 -c "import json;print(json.load(open('$RDD_KILLSWITCH')).get('enabled', True))" 2>/dev/null || echo "True")
    if [ "$enabled" = "False" ]; then
      return 1
    fi
  fi
  return 0
}

rdd_require_gate() {
  if ! rdd_gate_enabled; then
    echo "⚠  RDD GATE DISABLED (kill switch). Skipping gate."
    return 0
  fi
  local receipt="$RDD_FREEZE_DIR/$(date +%Y%m%d)-${1:-none}.receipt.json"
  if [ ! -f "$receipt" ]; then
    echo "❌ RDD GATE: no receipt for '${1:-none}'. Run: scripts/rdd/receipt.sh '$1'"
    return 1
  fi
  local allowed
  allowed=$(python3 -c "import json;print(json.load(open('$receipt')).get('authorization',{}).get('allowed_to_commit', False))" 2>/dev/null || echo "False")
  if [ "$allowed" != "True" ]; then
    echo "❌ RDD GATE: receipt exists but commit NOT authorized."
    return 1
  fi
  echo "✅ RDD GATE: receipt OK — commit authorized."
  return 0
}
