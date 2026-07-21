#!/bin/bash
# Instalar cron jobs para el sistema autónomo 24/7
# Ejecutar: bash scripts/install-cron.sh

REPO="$(cd "$(dirname "$0")/.." && pwd)"
CRON_FILE="/tmp/sdc-crontab"
cat > "$CRON_FILE" << CRONEOF
# ── Sonora Digital Corp — Daily Autonomous Pipeline ──
# Runs every morning at 8:00 AM
0 8 * * * $REPO/scripts/daily-pipeline.sh >> $REPO/state/logs/daily-cron.log 2>&1

# Git sync cada hora
0 * * * * cd $REPO && git pull origin main >> $REPO/state/logs/git-sync.log 2>&1

# Backup diario a las 3 AM
0 3 * * * $REPO/scripts/backup.sh >> $REPO/state/logs/backup-cron.log 2>&1

# Reporte ABE Music semanal (lunes 9 AM)
30 9 * * 1 $REPO/scripts/abe-report-push.sh >> $REPO/state/logs/abe-report-cron.log 2>&1

# Cleanup logs viejos (diario a las 2 AM)
0 2 * * * find $REPO/state/logs -name "*.log" -mtime +14 -delete

# Healthcheck cada 15 min
*/15 * * * * $REPO/scripts/autonomous.sh >> $REPO/state/logs/healthcheck-cron.log 2>&1

# Memory auto-save cada hora
0 * * * * cd $REPO && python3 scripts/automation/memory-save.py >> $REPO/state/logs/auto-save.log 2>&1

# Evolution Engine cada 6 horas (HAS-008)
0 */6 * * * $REPO/scripts/evolution-cron.sh >> $REPO/state/logs/evolution-cron.log 2>&1

# Disk alert
*/10 * * * * df -h / | awk 'NR==2 {if ($5+0 > 85) print "DISK ALERT: "$5}' >> /var/log/disk-alert.log
CRONEOF
EOF

crontab "$CRON_FILE"
rm "$CRON_FILE"
echo "✅ Cron jobs instalados:"
crontab -l
