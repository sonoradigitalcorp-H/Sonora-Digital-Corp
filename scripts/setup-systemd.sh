#!/bin/bash
# JARVIS Systemd Service Setup
# Creates systemd services for all JARVIS components
set -euo pipefail

JARVIS_DIR="${JARVIS_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
SERVICES_DIR="${SERVICES_DIR:-/etc/systemd/system}"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

if [ "$EUID" -ne 0 ]; then
    log "Please run as root (sudo)"
    exit 1
fi

log "Setting up JARVIS systemd services..."

# 1. JARVIS Core Orchestrator
cat > "${SERVICES_DIR}/jarvis-core.service" << 'EOF'
[Unit]
Description=JARVIS Core Orchestrator
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=mystic
WorkingDirectory=/home/mystic/sonora-digital-corp
ExecStart=/home/mystic/sonora-digital-corp/venv/bin/python main.py
Restart=always
RestartSec=10
Environment="PYTHONUNBUFFERED=1"
StandardOutput=append:/home/mystic/sonora-digital-corp/state/logs/core.log
StandardError=append:/home/mystic/sonora-digital-corp/state/logs/core.log

[Install]
WantedBy=multi-user.target
EOF

# 2. JARVIS Web UI
cat > "${SERVICES_DIR}/jarvis-webui.service" << 'EOF'
[Unit]
Description=JARVIS Web UI
After=network.target jarvis-core.service
Wants=jarvis-core.service

[Service]
Type=simple
User=mystic
WorkingDirectory=/home/mystic/sonora-digital-corp
ExecStart=/home/mystic/sonora-digital-corp/venv/bin/python webui/fastapp.py
Restart=always
RestartSec=10
Environment="PYTHONUNBUFFERED=1"
StandardOutput=append:/home/mystic/sonora-digital-corp/state/logs/webui.log
StandardError=append:/home/mystic/sonora-digital-corp/state/logs/webui.log

[Install]
WantedBy=multi-user.target
EOF

# 3. JARVIS Health Check Timer (runs every 5 minutes)
cat > "${SERVICES_DIR}/jarvis-healthcheck.service" << 'EOF'
[Unit]
Description=JARVIS Health Check

[Service]
Type=oneshot
User=mystic
ExecStart=/home/mystic/sonora-digital-corp/scripts/healthcheck.sh
StandardOutput=append:/home/mystic/sonora-digital-corp/state/logs/healthcheck.log
StandardError=append:/home/mystic/sonora-digital-corp/state/logs/healthcheck.log
EOF

cat > "${SERVICES_DIR}/jarvis-healthcheck.timer" << 'EOF'
[Unit]
Description=JARVIS Health Check Timer
Requires=jarvis-healthcheck.service

[Timer]
OnUnitActiveSec=5min
Unit=jarvis-healthcheck.service

[Install]
WantedBy=timers.target
EOF

# 4. JARVIS Backup Timer (runs daily at 3 AM)
cat > "${SERVICES_DIR}/jarvis-backup.service" << 'EOF'
[Unit]
Description=JARVIS Daily Backup

[Service]
Type=oneshot
User=mystic
ExecStart=/home/mystic/sonora-digital-corp/scripts/backup.sh
StandardOutput=append:/home/mystic/sonora-digital-corp/state/logs/backup.log
StandardError=append:/home/mystic/sonora-digital-corp/state/logs/backup.log
EOF

cat > "${SERVICES_DIR}/jarvis-backup.timer" << 'EOF'
[Unit]
Description=JARVIS Daily Backup Timer
Requires=jarvis-backup.service

[Timer]
OnCalendar=daily
Persistent=true
Unit=jarvis-backup.service

[Install]
WantedBy=timers.target
EOF

# Enable services
log "Enabling services..."
systemctl daemon-reload

services=(
    "jarvis-core.service"
    "jarvis-webui.service"
    "jarvis-healthcheck.timer"
    "jarvis-backup.timer"
)

for svc in "${services[@]}"; do
    systemctl enable "${svc}"
    log "  Enabled: ${svc}"
done

log "=" * 50
log "Systemd services installed!"
log "Start with:"
log "  sudo systemctl start jarvis-core.service"
log "  sudo systemctl start jarvis-webui.service"
log "  sudo systemctl start jarvis-healthcheck.timer"
log "  sudo systemctl start jarvis-backup.timer"
log ""
log "Check status:"
log "  sudo systemctl status jarvis-core.service"
log "  sudo systemctl status jarvis-webui.service"
log "  systemctl list-timers --all | grep jarvis"
log "=" * 50
