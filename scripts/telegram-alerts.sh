#!/bin/bash
# Telegram Alert System — Security + Health monitoring
# Runs via cron every 15 minutes
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$BASE_DIR/.env"

# Load tokens
if [ -f "$ENV_FILE" ]; then
  set -a; source "$ENV_FILE"; set +a
fi

BOT_TOKEN="${ABE_TELEGRAM_TOKEN:-}"
CHAT_ID="${ABE_TELEGRAM_CHAT:-}"
HOSTNAME="$(hostname)"
IP="149.56.46.173"
LOG_DIR="$BASE_DIR/state/logs"
ALERT_LOG="$LOG_DIR/telegram-alerts.log"

mkdir -p "$LOG_DIR"

send_alert() {
  local level="$1"
  local message="$2"
  local emoji=""
  case "$level" in
    CRITICAL) emoji="🚨";;
    WARNING)  emoji="⚠️";;
    INFO)     emoji="ℹ️";;
    RECOVERY) emoji="✅";;
  esac
  
  local text="${emoji} *${level}* — ${HOSTNAME}
${message}
_$(date '+%Y-%m-%d %H:%M:%S UTC')_"
  
  if [ -n "$BOT_TOKEN" ] && [ -n "$CHAT_ID" ]; then
    curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
      -d "chat_id=${CHAT_ID}" \
      -d "text=${text}" \
      -d "parse_mode=Markdown" \
      -d "disable_notification=false" > /dev/null 2>&1 || true
  fi
  
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message" >> "$ALERT_LOG"
}

# ── Health Checks ──

# 1. Docker containers
UNHEALTHY=$(docker ps --format '{{.Names}}\t{{.Status}}' 2>/dev/null | grep -v "healthy" | grep -v "Up " || true)
if echo "$UNHEALTHY" | grep -q "unhealthy"; then
  CONTAINERS=$(echo "$UNHEALTHY" | awk -F'\t' '{print $1}')
  send_alert "WARNING" "Containers unhealthy: $(echo $CONTAINERS | tr '\n' ' ')"
fi

# 2. Disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | tr -d '%')
if [ "$DISK_USAGE" -gt 85 ]; then
  send_alert "CRITICAL" "Disk at ${DISK_USAGE}% — needs cleanup"
elif [ "$DISK_USAGE" -gt 75 ]; then
  send_alert "WARNING" "Disk at ${DISK_USAGE}% — approaching limit"
fi

# 3. Memory
MEM_USED=$(free | awk '/Mem:/ {printf "%.0f", $3/$2 * 100}')
if [ "$MEM_USED" -gt 90 ]; then
  send_alert "CRITICAL" "Memory at ${MEM_USED}% — OOM risk"
elif [ "$MEM_USED" -gt 80 ]; then
  send_alert "WARNING" "Memory at ${MEM_USED}%"
fi

# 4. WebUI health
if ! curl -sf http://127.0.0.1:5174/api/enterprise-score > /dev/null 2>&1; then
  send_alert "CRITICAL" "JARVIS WebUI not responding on :5174"
fi

# 5. Nginx health
if ! curl -sf https://sonoradigitalcorp.com > /dev/null 2>&1; then
  send_alert "CRITICAL" "Nginx / main domain not responding"
fi

# 6. fail2ban status
BANNED=$(sudo fail2ban-client status sshd 2>/dev/null | grep "Banned IP list" | grep -oP '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | wc -l || echo 0)
if [ "$BANNED" -gt 0 ]; then
  send_alert "INFO" "Fail2ban: $BANNED IPs currently banned on sshd"
fi

# 7. SSL expiry
for domain in sonoradigitalcorp.com api.sonoradigitalcorp.com n8n.sonoradigitalcorp.com; do
  EXPIRY=$(echo | openssl s_client -servername "$domain" -connect "$domain:443" 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
  if [ -n "$EXPIRY" ]; then
    EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s 2>/dev/null)
    NOW_EPOCH=$(date +%s)
    DAYS_LEFT=$(( (EXPIRY_EPOCH - NOW_EPOCH) / 86400 ))
    if [ "$DAYS_LEFT" -lt 14 ]; then
      send_alert "WARNING" "SSL for $domain expires in $DAYS_LEFT days"
    fi
  fi
done

# 8. Git sync status
cd "$BASE_DIR" 2>/dev/null || true
GIT_STATUS=$(git log --oneline origin/main..HEAD 2>/dev/null | wc -l)
if [ "$GIT_STATUS" -gt 0 ]; then
  send_alert "WARNING" "$GIT_STATUS local commits not pushed to origin/main"
fi

# 9. Port scan — unexpected open ports
EXPECTED="22 80 443"
ALL_PORTS=$(sudo ss -tlnp 2>/dev/null | grep -oP '0\.0\.0\.0:(\d+)' | cut -d: -f2 | sort -u || echo "")
for port in $ALL_PORTS; do
  if ! echo "$EXPECTED" | grep -q "$port"; then
    send_alert "WARNING" "Unexpected open port: $port (0.0.0.0)"
  fi
done

# Done — log healthy state
echo "[$(date '+%Y-%m-%d %H:%M:%S')] [OK] All checks passed. Disk: ${DISK_USAGE}% Mem: ${MEM_USED}% Banned: $BANNED" >> "$ALERT_LOG"
