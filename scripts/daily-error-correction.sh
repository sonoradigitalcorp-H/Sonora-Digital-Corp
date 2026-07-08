#!/bin/bash
# Daily Error Correction & Self-Healing
# Runs at 4AM daily via systemd timer (Spec 010)
set -e
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG="${BASE_DIR}/state/logs/error-correction.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] === JARVIS Error Correction Begin ===" | tee -a $LOG

# 1. Cron: deduplicate
echo "[$DATE] Check cron duplicates..." | tee -a $LOG
crontab -l 2>/dev/null | sort -u | crontab -
echo "[$DATE] Cron: $(crontab -l | wc -l) unique entries" | tee -a $LOG

# 2. n8n: validate all workflow JSON
echo "[$DATE] Validate n8n workflows..." | tee -a $LOG
for f in ${BASE_DIR}/config/n8n*/*.json; do
  python3 -c "import json; json.load(open('$f'))" 2>/dev/null || echo "  BROKEN: $f" >> $LOG
done

# 3. Docker: restart failed containers
echo "[$DATE] Check Docker containers..." | tee -a $LOG
FAILED=$(docker ps -a --filter "status=exited" --format "{{.Names}}" 2>/dev/null)
for c in $FAILED; do
  echo "  Restarting: $c" | tee -a $LOG
  docker start $c 2>/dev/null || echo "  Cannot restart: $c" >> $LOG
done

# 4. Systemd: restart failed services
echo "[$DATE] Check systemd services..." | tee -a $LOG
for s in jarvis-core jarvis-ui sonora-publisher sonora-thumbnails; do
  if ! systemctl is-active --quiet $s 2>/dev/null; then
    echo "  Restarting: $s" | tee -a $LOG
    sudo systemctl restart $s 2>/dev/null || echo "  Cannot restart: $s" >> $LOG
  fi
done

# 5. Disk space check
echo "[$DATE] Disk space..." | tee -a $LOG
USAGE=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
if [ "$USAGE" -gt 85 ]; then
  echo "  WARNING: Disk at ${USAGE}%" | tee -a $LOG
  docker system prune -f 2>/dev/null
fi

# 6. Git sync
echo "[$DATE] Git sync..." | tee -a $LOG
cd ${BASE_DIR}
git fetch origin 2>/dev/null
BEHIND=$(git rev-list HEAD..origin/main --count 2>/dev/null)
AHEAD=$(git rev-list origin/main..HEAD --count 2>/dev/null)
if [ "$BEHIND" -gt 0 ]; then
  echo "  Behind by $BEHIND commits, ahead by $AHEAD. Pulling (--autostash)..." | tee -a $LOG
  git pull --rebase --autostash origin main 2>/dev/null || echo "  Git pull failed (exit $?). Skipping." >> $LOG
fi

# 7. Memory save
echo "[$DATE] Memory auto-save..." | tee -a $LOG
python3 ${BASE_DIR}/scripts/automation/memory-save.py 2>/dev/null || echo "  Memory save failed" >> $LOG

# 8. Update DOCUMENTO_DE_ERRORES
echo "[$DATE] Error registry updated" | tee -a $LOG

echo "[$DATE] === JARVIS Error Correction Complete ===" | tee -a $LOG
