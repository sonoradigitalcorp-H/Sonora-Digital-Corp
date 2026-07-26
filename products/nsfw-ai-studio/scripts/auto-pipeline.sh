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

echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  PIPELINE AUTOMÁTICO NSFW AI STUDIO${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# --- Configuración interactiva ---
read -p "Nombre del personaje/profesor: " CHARACTER_NAME
if [ -z "$CHARACTER_NAME" ]; then
    error "Nombre obligatorio"
    exit 1
fi

read -p "Modelo base (flux/sdxl) [${LORA_BASE_MODEL:-flux}]: " MODEL
MODEL=${MODEL:-${LORA_BASE_MODEL:-flux}}

read -p "Prompt para el video: " VIDEO_PROMPT
if [ -z "$VIDEO_PROMPT" ]; then
    error "Prompt obligatorio"
    exit 1
fi

read -p "Ruta del archivo de audio para lip-sync (opcional): " AUDIO_FILE
read -p "¿Entrenar LoRA nuevo? (s/N): " TRAIN_LORA
TRAIN_LORA=${TRAIN_LORA:-n}

echo ""
log "=== PIPELINE: $CHARACTER_NAME ==="
log "Modelo: $MODEL"
log "Prompt: $VIDEO_PROMPT"
[ -n "$AUDIO_FILE" ] && log "Audio:  $AUDIO_FILE"
log "LoRA:   $([ "$TRAIN_LORA" = "s" ] || [ "$TRAIN_LORA" = "S" ] && echo "Entrenar nuevo" || echo "Usar existente")"
echo ""

# --- Paso 1: Entrenar LoRA (opcional) ---
if [ "$TRAIN_LORA" = "s" ] || [ "$TRAIN_LORA" = "S" ]; then
    echo ""
    log "[1/3] Entrenando LoRA para '$CHARACTER_NAME'..."
    echo ""

    DATASET_DIR="$PROJECT_DIR/datasets/$CHARACTER_NAME"
    if [ ! -d "$DATASET_DIR" ]; then
        warn "No hay dataset en $DATASET_DIR"
        info "Crea el directorio y pon tus imágenes allí (mínimo 20)"
        read -p "Presiona Enter cuando esté listo..."
    fi

    bash "$SCRIPT_DIR/train-lora.sh" \
        --name "$CHARACTER_NAME" \
        --model "$MODEL" \
        --tool kohya

    log "LoRA entrenado. Copiando a modelos..."
    cp "$PROJECT_DIR/output/loras/$CHARACTER_NAME"/*.safetensors "$PROJECT_DIR/models/loras/" 2>/dev/null || warn "No se pudo copiar el LoRA"
fi

# --- Paso 2: Generar video ---
echo ""
log "[2/3] Generando video..."
echo ""

WORKFLOW_FILE="$PROJECT_DIR/configs/workflow-templates/animatediff.json"
if [ ! -f "$WORKFLOW_FILE" ]; then
    warn "Workflow template no encontrado: $WORKFLOW_FILE"
    info "Usando workflow por defecto de ComfyUI..."
    WORKFLOW_FILE=""
fi

if [ -n "$WORKFLOW_FILE" ]; then
    bash "$SCRIPT_DIR/generate-video.sh" \
        --workflow "$WORKFLOW_FILE" \
        --prompt "$VIDEO_PROMPT" \
        --lora "$CHARACTER_NAME" \
        --output "${CHARACTER_NAME}_video" || warn "Generación de video falló"
else
    warn "Saltando generación de video (sin workflow)"
fi

# --- Paso 3: Lip-sync (opcional) ---
if [ -n "$AUDIO_FILE" ] && [ -f "$AUDIO_FILE" ]; then
    echo ""
    log "[3/3] Sincronizando lip-sync..."
    echo ""

    # Buscar el video generado más reciente
    LATEST_VIDEO=$(ls -t "$PROJECT_DIR/output"/*.mp4 2>/dev/null | head -1)

    if [ -n "$LATEST_VIDEO" ]; then
        bash "$SCRIPT_DIR/sync-lips.sh" \
            --video "$LATEST_VIDEO" \
            --audio "$AUDIO_FILE" \
            --output "${CHARACTER_NAME}_clase" \
            --tool "${LIPSYNC_MODEL:-musetalk}" || warn "Lip-sync falló"
    else
        warn "No se encontró video para lip-sync"
    fi
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  PIPELINE COMPLETADO!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Outputs:"
echo -e "  LoRA:    ${CYAN}$PROJECT_DIR/output/loras/$CHARACTER_NAME/${NC}"
echo -e "  Video:   ${CYAN}$PROJECT_DIR/output/$(ls -t "$PROJECT_DIR/output"/*.mp4 2>/dev/null | head -1)${NC}"
echo ""
echo -e "Próximos pasos:"
echo -e "  1. Revisa el video en output/"
echo -e "  2. Edita en ComfyUI: ${CYAN}http://localhost:${COMFYUI_PORT:-8188}${NC}"
echo -e "  3. Entrena más LoRAs: ${CYAN}make train-lora${NC}"
echo ""
