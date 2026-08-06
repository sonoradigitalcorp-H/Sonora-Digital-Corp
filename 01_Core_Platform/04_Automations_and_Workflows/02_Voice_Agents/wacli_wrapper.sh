#!/usr/bin/env bash
# wacli_wrapper.sh - Wrapper para integración WhatsApp de Sonora Digital Corp
# Usa wacli para recibir y enviar mensajes de voz.
set -euo pipefail

WACLI="${WACLI:-wacli}"
DEFAULT_TENANT="${DEFAULT_TENANT:-Aztrotech}"
LOG_DIR="00_Administration/Session_Logs"

mkdir -p "$LOG_DIR"

log() {
    echo "[$(date -Iseconds)] $*" | tee -a "$LOG_DIR/whatsapp_pipeline.log"
}

case "${1:-receive}" in
    receive)
        log "Esperando mensaje de audio de WhatsApp..."
        "$WACLI" receive --format json 2>&1 | tee -a "$LOG_DIR/whatsapp_last.json"
        ;;
    send)
        AUDIO="${2:?Audio file path required}"
        TO="${3:-$DEFAULT_TENANT}"
        log "Enviando audio a $TO: $AUDIO"
        "$WACLI" send --audio "$AUDIO" --to "$TO" 2>&1 | tee -a "$LOG_DIR/whatsapp_send.log"
        ;;
    status)
        log "Estado de wacli:"
        "$WACLI" status 2>&1 || echo "wacli no responde"
        ;;
    *)
        echo "Uso: wacli_wrapper.sh [receive|send <audio> <to>|status]"
        exit 1
        ;;
esac
