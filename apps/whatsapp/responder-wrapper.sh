#!/bin/bash
# WhatsApp Responder wrapper — loads env vars before starting
# Used by systemd to set OPENROUTER_API_KEY and FOUNDER_PHONE

REPO="/home/ubuntu/sonora-digital-corp"
ENV_FILE="$REPO/.env.whatsapp"

if [ -f "$ENV_FILE" ]; then
    set -a
    source "$ENV_FILE"
    set +a
fi

cd "$REPO"
PYTHONPATH="$REPO" exec /usr/bin/python3 "$REPO/apps/whatsapp/responder.py" "$@"
