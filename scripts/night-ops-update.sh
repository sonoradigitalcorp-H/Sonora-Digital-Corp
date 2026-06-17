#!/bin/bash
# Update night-ops dashboard and commit progress
cd /home/mystic/sonora-digital-corp
LOG_FILE="logs/night-ops.log"

echo "[$(date)] === Night Ops Progress Update ===" >> "$LOG_FILE"

# Check what's running
echo "Services:" >> "$LOG_FILE"
for port in 5174 7456 8000 18990; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port --connect-timeout 2 2>/dev/null || echo "DOWN")
  echo "  Port $port: $STATUS" >> "$LOG_FILE"
done

# Check Docker
echo "Docker:" >> "$LOG_FILE"
docker ps --format "{{.Names}}: {{.Status}}" >> "$LOG_FILE" 2>/dev/null

# Update the HTML dashboard with current phase info
# (dashboard auto-refreshes every 5 min via meta refresh)

# Check for new errors
echo "Errors:" >> "$LOG_FILE"
grep -c "ERROR\|FAIL\|BROKEN" logs/error-correction.log 2>/dev/null || echo "0" >> "$LOG_FILE"

# Auto-commit if significant changes
git add config/n8n-zero-token/ logs/ 2>/dev/null
git diff --cached --quiet || git commit -m "auto: night ops progress $(date +%H:%M)" 2>/dev/null
git push origin main 2>/dev/null

echo "[$(date)] Progress saved" >> "$LOG_FILE"
