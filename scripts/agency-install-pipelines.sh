#!/bin/bash
# AGENCY OS — Instalación de Pipelines Automáticos
# Configura: systemd timers + cron jobs para automatización
# Ejecuta: Una vez (o cuando cambien los servicios)
set -euo pipefail

echo "=== AGENCY OS — Instalando Pipelines ==="

SCRIPTS="/home/mystic/sonora-digital-corp/scripts"
SYSTEMD="/etc/systemd/system"

# === 1. AGENCY PIPELINE (diario 4AM) ===
echo "[1/4] Agency pipeline timer (4AM daily)..."
cat << 'EOF' | sudo tee "$SYSTEMD/agency-pipeline.service" > /dev/null
[Unit]
Description=AGENCY OS — Daily Auto-Improve Pipeline
After=network.target docker.service

[Service]
Type=oneshot
ExecStart=/home/mystic/sonora-digital-corp/scripts/agency-pipeline.sh
User=mystic
WorkingDirectory=/home/mystic/sonora-digital-corp
StandardOutput=append:/home/mystic/sonora-digital-corp/state/logs/agency-pipeline.log
StandardError=append:/home/mystic/sonora-digital-corp/state/logs/agency-pipeline.log
EOF

cat << 'EOF' | sudo tee "$SYSTEMD/agency-pipeline.timer" > /dev/null
[Unit]
Description=AGENCY OS — Daily 4AM Pipeline

[Timer]
OnCalendar=*-*-* 04:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

# === 2. GIT AUTO-SYNC (cada hora) ===
echo "[2/4] Git auto-sync cron (hourly)..."
cat << 'EOF' | sudo tee "$SYSTEMD/agency-git-sync.service" > /dev/null
[Unit]
Description=AGENCY OS — Hourly Git Sync
After=network.target

[Service]
Type=oneshot
ExecStart=/home/mystic/sonora-digital-corp/scripts/agency-github-sync.sh
User=mystic
WorkingDirectory=/home/mystic/sonora-digital-corp
StandardOutput=append:/home/mystic/sonora-digital-corp/state/logs/git-sync.log
StandardError=append:/home/mystic/sonora-digital-corp/state/logs/git-sync.log
EOF

cat << 'EOF' | sudo tee "$SYSTEMD/agency-git-sync.timer" > /dev/null
[Unit]
Description=AGENCY OS — Hourly Git Sync

[Timer]
OnCalendar=*-*-* *:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

# === 3. E2E NOCTURNO ===
echo "[3/4] E2E nightly simulation..."
cat << 'EOF' | sudo tee "$SYSTEMD/agency-e2e-nightly.service" > /dev/null
[Unit]
Description=AGENCY OS — Nightly E2E User Simulation
After=network.target

[Service]
Type=oneshot
ExecStart=/home/mystic/sonora-digital-corp/scripts/agency-e2e-simulate.sh
User=mystic
WorkingDirectory=/home/mystic/sonora-digital-corp
Environment=DISPLAY=:0
StandardOutput=append:/home/mystic/sonora-digital-corp/state/logs/e2e-nightly.log
StandardError=append:/home/mystic/sonora-digital-corp/state/logs/e2e-nightly.log
EOF

cat << 'EOF' | sudo tee "$SYSTEMD/agency-e2e-nightly.timer" > /dev/null
[Unit]
Description=AGENCY OS — Nightly E2E at 3AM

[Timer]
OnCalendar=*-*-* 03:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

# === 4. ENABLE TODO ===
echo "[4/4] Enabling timers..."
sudo systemctl daemon-reload
for timer in agency-pipeline agency-git-sync agency-e2e-nightly; do
    sudo systemctl enable --now "$timer.timer" 2>/dev/null && echo "  ✅ $timer.timer enabled" || echo "  ⚠️  $timer.timer failed (try: sudo systemctl enable $timer.timer)"
done

echo ""
echo "=== Pipelines instalados ==="
echo "  agency-pipeline.timer  →  Daily 04:00"
echo "  agency-git-sync.timer  →  Hourly"
echo "  agency-e2e-nightly.timer → Nightly 03:00"
echo ""
echo "Para ver estado: systemctl list-timers 'agency-*'"
echo "Para probar:     sudo systemctl start agency-pipeline.service"
