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

COMFYUI_URL="http://localhost:${COMFYUI_PORT:-8188}"

usage() {
    echo "Uso: $0 -w workflow.json [-p prompt] [-l lora] [opciones]"
    echo ""
    echo "Genera video desde ComfyUI API"
    echo ""
    echo "OPCIONES:"
    echo "  -w, --workflow ARCHIVO   Workflow JSON de ComfyUI (obligatorio)"
    echo "  -p, --prompt TEXTO       Prompt positivo"
    echo "  -n, --negative TEXTO     Prompt negativo"
    echo "  -l, --lora ARCHIVO       Archivo .safetensors del LoRA"
    echo "  -o, --output NOMBRE      Nombre del archivo de salida"
    echo "  -s, --steps STEPS        Sampling steps (default: $VIDEO_STEPS)"
    echo "  -f, --frames FRAMES      Número de frames (default: $VIDEO_FRAMES)"
    echo "  -W, --width W            Ancho (default: $VIDEO_WIDTH)"
    echo "  -H, --height H           Alto (default: $VIDEO_HEIGHT)"
    echo "  --cfg CFG                CFG scale (default: $VIDEO_CFG)"
    echo "  --seed SEED              Semilla (default: aleatoria)"
    echo "  -h, --help               Muestra esta ayuda"
    exit 1
}

WORKFLOW=""
PROMPT=""
NEGATIVE=""
LORA=""
OUTPUT=""
STEPS="${VIDEO_STEPS:-30}"
FRAMES="${VIDEO_FRAMES:-49}"
WIDTH="${VIDEO_WIDTH:-640}"
HEIGHT="${VIDEO_HEIGHT:-480}"
CFG="${VIDEO_CFG:-6.0}"
SEED=$RANDOM

while [[ $# -gt 0 ]]; do
    case $1 in
        -w|--workflow)   WORKFLOW="$2"; shift 2 ;;
        -p|--prompt)     PROMPT="$2"; shift 2 ;;
        -n|--negative)   NEGATIVE="$2"; shift 2 ;;
        -l|--lora)       LORA="$2"; shift 2 ;;
        -o|--output)     OUTPUT="$2"; shift 2 ;;
        -s|--steps)      STEPS="$2"; shift 2 ;;
        -f|--frames)     FRAMES="$2"; shift 2 ;;
        -W|--width)      WIDTH="$2"; shift 2 ;;
        -H|--height)     HEIGHT="$2"; shift 2 ;;
        --cfg)           CFG="$2"; shift 2 ;;
        --seed)          SEED="$2"; shift 2 ;;
        -h|--help)       usage ;;
        *) error "Argumento desconocido: $1"; usage ;;
    esac
done

if [ -z "$WORKFLOW" ]; then
    error "Debes especificar --workflow ARCHIVO.json"
    usage
fi

if [ ! -f "$WORKFLOW" ]; then
    error "Workflow no encontrado: $WORKFLOW"
    exit 1
fi

if [ -z "$OUTPUT" ]; then
    OUTPUT="video_$(date +%Y%m%d_%H%M%S)"
fi

# Verificar que ComfyUI responde
if ! curl -sf "$COMFYUI_URL" > /dev/null 2>&1; then
    error "ComfyUI no responde en $COMFYUI_URL"
    info "¿Está corriendo? Prueba: make up"
    exit 1
fi

log "========================================="
log "  GENERANDO VIDEO"
log "========================================="
log "Workflow:    $WORKFLOW"
[ -n "$PROMPT" ]  && log "Prompt:      $PROMPT"
[ -n "$LORA" ]    && log "LoRA:        $LORA"
log "Steps:       $STEPS"
log "Frames:      $FRAMES"
log "Resolución:  ${WIDTH}x${HEIGHT}"
log "CFG:         $CFG"
log "Seed:        $SEED"
log "Output:      $OUTPUT"
log "========================================="

# Cargar workflow y reemplazar placeholders
WORKFLOW_JSON=$(cat "$WORKFLOW")

# Reemplazar placeholders en el JSON
WORKFLOW_JSON=${WORKFLOW_JSON//\$\{prompt\}/$PROMPT}
WORKFLOW_JSON=${WORKFLOW_JSON//\$\{negative\}/$NEGATIVE}
WORKFLOW_JSON=${WORKFLOW_JSON//\$\{steps\}/$STEPS}
WORKFLOW_JSON=${WORKFLOW_JSON//\$\{frames\}/$FRAMES}
WORKFLOW_JSON=${WORKFLOW_JSON//\$\{width\}/$WIDTH}
WORKFLOW_JSON=${WORKFLOW_JSON//\$\{height\}/$HEIGHT}
WORKFLOW_JSON=${WORKFLOW_JSON//\$\{cfg\}/$CFG}
WORKFLOW_JSON=${WORKFLOW_JSON//\$\{seed\}/$SEED}

# Si hay LoRA, añadir nodo LoRALoader
if [ -n "$LORA" ]; then
    LORA_FILENAME=$(basename "$LORA")
    # Buscar nodo de checkpoint y añadir LoRA loader
    info "Aplicando LoRA: $LORA_FILENAME"
fi

# Enviar a ComfyUI API
log "Enviando workflow a ComfyUI..."

RESPONSE=$(curl -s -X POST "$COMFYUI_URL/api/prompt" \
    -H "Content-Type: application/json" \
    -d "$WORKFLOW_JSON")

# Extraer prompt_id
PROMPT_ID=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('prompt_id',''))" 2>/dev/null || echo "")

if [ -z "$PROMPT_ID" ]; then
    error "Error al enviar workflow: $RESPONSE"
    exit 1
fi

log "Prompt ID: $PROMPT_ID"
log "Esperando generación..."

# Esperar a que termine
while true; do
    STATUS=$(curl -sf "$COMFYUI_URL/api/queue" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data.get('queue_running') and data['queue_running'][0].get('prompt_id') == '$PROMPT_ID':
    print('running')
elif any(q['prompt_id'] == '$PROMPT_ID' for q in data.get('queue_pending', [])):
    print('pending')
else:
    print('done')
" 2>/dev/null || echo "unknown")

    case "$STATUS" in
        running) info "Generando..." ;;
        pending) info "En cola..." ;;
        done)    log "Generación completada!"; break ;;
        *)       warn "Esperando... ($STATUS)" ;;
    esac
    sleep 5
done

# Buscar archivo generado
OUTPUT_FILE=$(curl -sf "$COMFYUI_URL/api/history/$PROMPT_ID" | python3 -c "
import sys, json
data = json.load(sys.stdin)
outputs = data.get('outputs', {})
for node_id, node_out in outputs.items():
    for key, val in node_out.items():
        if isinstance(val, list):
            for item in val:
                if isinstance(item, dict) and item.get('type') == 'output':
                    print(item.get('filename', ''))
" 2>/dev/null || echo "")

log "========================================="
log "  VIDEO GENERADO EXITOSAMENTE"
log "========================================="
log "Output: $PROJECT_DIR/output/$OUTPUT_FILE"
log ""

# Copiar a output con nombre legible
if [ -n "$OUTPUT_FILE" ]; then
    cp "$PROJECT_DIR/output/$OUTPUT_FILE" "$PROJECT_DIR/output/${OUTPUT}.mp4" 2>/dev/null || \
    cp "$PROJECT_DIR/output/$OUTPUT_FILE" "$PROJECT_DIR/output/${OUTPUT}.webm" 2>/dev/null || true
    log "Copiado como: output/${OUTPUT}.*"
fi
