#!/bin/bash
# WhatsApp Webhook cron — ensure webhook listener is running
# Usage: add to crontab: */5 * * * * /bin/bash /home/mystic/sonora-digital-corp/scripts/whatsapp-webhook-cron.sh

REPO="/home/mystic/sonora-digital-corp"
PIDFILE="/tmp/whatsapp-webhook.pid"
LOGFILE="$REPO/state/logs/whatsapp-webhook.log"

mkdir -p "$REPO/state/logs"

if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    echo "[$(date -Iseconds)] whatsapp-webhook already running" >> "$LOGFILE"
    exit 0
fi

cd "$REPO" || exit 1
PYTHONPATH=. nohup python3 apps/whatsapp/webhook.py >> "$LOGFILE" 2>&1 &
echo $! > "$PIDFILE"
echo "[$(date -Iseconds)] whatsapp-webhook started" >> "$LOGFILE"
