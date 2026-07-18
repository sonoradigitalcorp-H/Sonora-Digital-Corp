#!/usr/bin/env bash
# ops-agent — Ops Harness systemd service wrapper
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="$PWD"

# Monitor loop (infinite, runs every 5 min)
while true; do
    python3 -m ops.monitor --once
    python3 -m ops.backup
    sleep 300
done
