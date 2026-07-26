#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
source "$PROJECT_DIR/.env" 2>/dev/null || true

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log()   { echo -e "${GREEN}[+]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[x]${NC} $1"; }
info()  { echo -e "${CYAN}[i]${NC} $1"; }

usage() {
    echo "Uso: $0 -v video.mp4 -a audio.mp3 [-o output.mp4] [-t tool]"
    echo ""
    echo "Sincroniza labios de un video con un archivo de audio"
    echo ""
    echo "OPCIONES:"
    echo "  -v, --video ARCHIVO    Video de entrada (con rostro visible)"
    echo "  -a, --audio ARCHIVO    Audio para sincronizar"
    echo "  -o, --output NOMBRE    Archivo de salida (default: lipsync_YYYYMMDD_HHMMSS)"
    echo "  -t, --tool TOOL        musetalk | wav2lip (default: $LIPSYNC_MODEL)"
    echo "  -h, --help             Muestra esta ayuda"
    exit 1
}

VIDEO=""
AUDIO=""
OUTPUT=""
TOOL="${LIPSYNC_MODEL:-musetalk}"

while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--video)  VIDEO="$2"; shift 2 ;;
        -a|--audio)  AUDIO="$2"; shift 2 ;;
        -o|--output) OUTPUT="$2"; shift 2 ;;
        -t|--tool)   TOOL="$2"; shift 2 ;;
        -h|--help)   usage ;;
        *) error "Argumento desconocido: $1"; usage ;;
    esac
done

if [ -z "$VIDEO" ] || [ -z "$AUDIO" ]; then
    error "Debes especificar --video y --audio"
    usage
fi

if [ ! -f "$VIDEO" ]; then error "Video no encontrado: $VIDEO"; fi
if [ ! -f "$AUDIO" ]; then error "Audio no encontrado: $AUDIO"; fi

if [ -z "$OUTPUT" ]; then
    OUTPUT="lipsync_$(date +%Y%m%d_%H%M%S)"
fi

VIDEO_ABS=$(realpath "$VIDEO")
AUDIO_ABS=$(realpath "$AUDIO")
OUTPUT_DIR="$PROJECT_DIR/output"
mkdir -p "$OUTPUT_DIR"

log "========================================="
log "  LIP-SYNC: $OUTPUT"
log "========================================="
log "Tool:    $TOOL"
log "Video:   $VIDEO_ABS"
log "Audio:   $AUDIO_ABS"
log "Output:  $OUTPUT_DIR/${OUTPUT}.mp4"
log "========================================="

case "$TOOL" in
    musetalk)
        if ! docker ps --format '{{.Names}}' | grep -q nsfw-musetalk; then
            warn "MuseTalk no está corriendo."
            info "Ejecuta: docker compose --profile lipsync up -d musetalk"
            exit 1
        fi
        log "Enviando a MuseTalk (Gradio API)..."
        # MuseTalk usa API Gradio
        python3 -c "
import requests, json, time

resp = requests.post('http://localhost:${MUSETALK_PORT:-7861}/api/predict', json={
    'data': ['$VIDEO_ABS', '$AUDIO_ABS']
}).json()
print('Respuesta:', json.dumps(resp, indent=2))
" 2>&1 || warn "MuseTalk API falló. Usa la UI: http://localhost:${MUSETALK_PORT:-7861}"
        ;;

    wav2lip)
        if ! docker ps --format '{{.Names}}' | grep -q nsfw-wav2lip; then
            warn "Wav2Lip no está corriendo."
            info "Ejecuta: docker compose --profile lipsync up -d wav2lip"
            exit 1
        fi
        log "Enviando a Wav2Lip..."
        python3 -c "
import requests

with open('$VIDEO_ABS', 'rb') as vf, open('$AUDIO_ABS', 'rb') as af:
    resp = requests.post(
        'http://localhost:${WAV2LIP_PORT:-8000}/process',
        files={'video': vf, 'audio': af}
    ).json()
    print('Respuesta:', resp)
" 2>&1 || warn "Wav2Lip API falló. Revisa: http://localhost:${WAV2LIP_PORT:-8000}"
        ;;

    *)
        error "Tool desconocida: $TOOL (usa: musetalk, wav2lip)"
        exit 1
        ;;
esac

log "========================================="
log "  LIP-SYNC COMPLETADO"
log "========================================="
log "Output: $OUTPUT_DIR/${OUTPUT}.mp4"
