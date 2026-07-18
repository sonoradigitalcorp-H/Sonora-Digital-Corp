#!/usr/bin/env bash
# monitor-service — Ops Harness health checker
# Emite eventos al bus: system:service:up/down/recovered, system:disk:warning
set -euo pipefail
cd "$(dirname "$0")/.."
SDC_HOME="$PWD"
exec python3 -m ops.monitor
