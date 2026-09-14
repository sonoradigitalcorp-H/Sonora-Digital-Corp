#!/bin/bash
# deploy-proactive-scheduler.sh
# Deploy proactive scheduler to VPS Hostinger
# Run from laptop: bash deploy-proactive-scheduler.sh

set -euo pipefail

VPS="root@45.90.108.12"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REMOTE_DIR="/opt/hermes/scripts"

echo "📦 Deploying proactive scheduler to VPS..."

# Copy script
scp "${SCRIPT_DIR}/proactive_scheduler.py" "${VPS}:${REMOTE_DIR}/"
echo "✅ Script copied"

# Copy systemd files
scp "${SCRIPT_DIR}/proactive-scheduler.service" "${VPS}:/etc/systemd/system/"
scp "${SCRIPT_DIR}/proactive-scheduler.timer" "${VPS}:/etc/systemd/system/"
echo "✅ Systemd files copied"

# Enable and start timer
ssh "${VPS}" << 'REMOTE'
systemctl daemon-reload
systemctl enable --now proactive-scheduler.timer
echo "Timer status:"
systemctl status proactive-scheduler.timer --no-pager
echo ""
echo "Next run:"
systemctl list-timers proactive-scheduler.timer --no-pager
REMOTE

echo ""
echo "✅ Deploy complete!"
echo "   To test: ssh ${VPS} 'python3 /opt/hermes/scripts/proactive_scheduler.py --dry-run'"
echo "   To check: ssh ${VPS} 'systemctl list-timers proactive-scheduler.timer'"
