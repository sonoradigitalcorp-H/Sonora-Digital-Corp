#!/bin/bash
# Restaura .env desde ~/.secrets/sonora/ después de clonar
SECRETS="$HOME/.secrets/sonora"
REPO="$HOME/Documentos/Sonora Digital Corp/sonora-digital-corp"

[ -f "$SECRETS/apps/frontends.env" ] && cp "$SECRETS/apps/frontends.env" "$REPO/apps/frontends/app/.env"
[ -f "$SECRETS/config/sonora.env" ] && cp "$SECRETS/config/sonora.env" "$REPO/config/.env"
[ -f "$SECRETS/infra/infra.env" ] && cp "$SECRETS/infra/infra.env" "$REPO/infra/.env"
[ -f "$SECRETS/products/mystika-api.env" ] && cp "$SECRETS/products/mystika-api.env" "$REPO/products/mystika/api/.env"
[ -f "$SECRETS/products/mystika-telegram.env" ] && cp "$SECRETS/products/mystika-telegram.env" "$REPO/products/mystika/telegram-bot/.env"

echo "✅ Secrets restaurados"
echo "Los twins están en ~/.secrets/twins/"
