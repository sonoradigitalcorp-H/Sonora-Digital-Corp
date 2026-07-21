#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "$0")/.." && pwd)"
WACLI="$HOME/.local/bin/wacli"
STORE="$HOME/.config/ai.opencode.desktop/wacli"
AUDIO="$DIR/state/whatsapp/clients/r1/pending_cesar_audio.ogg"

echo "🔊 Enviando audio a César (6623446953)..."
echo "   Store: $STORE"
echo ""

# Sync first
echo "[1/2] Sincronizando WhatsApp..."
$WACLI --store "$STORE" --lock-wait=60s sync --max-db-size=1GB
echo "✅ Sync completo"
sleep 2

# Send
echo "[2/2] Enviando nota de voz..."
$WACLI --store "$STORE" send file \
  --file "$AUDIO" \
  --mime "audio/ogg; codecs=opus" \
  --ptt \
  --to "5216623446953@s.whatsapp.net" \
  --post-send-wait 20s
echo "✅ Audio enviado!"
