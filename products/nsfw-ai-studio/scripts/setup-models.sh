#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODELS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)/models"
source "$SCRIPT_DIR/../.env" 2>/dev/null || true

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()   { echo -e "${GREEN}[+]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[x]${NC} $1"; }

mkdir -p "$MODELS_DIR"/{checkpoints,loras,vae,controlnet,clip,upscale_models,animatediff}

download_model() {
    local url="$1"
    local dest="$2"
    local label="$3"
    if [ -f "$dest" ]; then
        warn "Ya existe: $label"
        return
    fi
    log "Descargando: $label"
    wget -q --show-progress -O "$dest" "$url" || error "Falló: $label"
}

if command -v huggingface-cli &>/dev/null; then
    USE_HF=true
else
    USE_HF=false
    warn "huggingface-cli no instalado. Usando wget directo."
fi

log "=== Descargando modelos base ==="

# --- Checkpoint (SDXL / Flux base) ---
if [ ! -f "$MODELS_DIR/checkpoints/flux1-dev.safetensors" ]; then
    if $USE_HF; then
        log "Descargando Flux.1 Dev..."
        huggingface-cli download black-forest-labs/FLUX.1-dev flux1-dev.safetensors --local-dir "$MODELS_DIR/checkpoints"
    fi
fi

# --- VAE ---
if [ ! -f "$MODELS_DIR/vae/FLUX.1-dev-vae.safetensors" ]; then
    log "Descargando VAE..."
    download_model \
        "https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/vae/diffusion_pytorch_model.safetensors" \
        "$MODELS_DIR/vae/FLUX.1-dev-vae.safetensors" \
        "Flux VAE"
fi

# --- Clip (necesario para Flux) ---
download_model \
    "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors" \
    "$MODELS_DIR/clip/clip_l.safetensors" \
    "CLIP-L"

download_model \
    "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp16.safetensors" \
    "$MODELS_DIR/clip/t5xxl_fp16.safetensors" \
    "T5XXL FP16"

# --- ControlNet (opcional pero recomendado para NSFW) ---
if [ ! -f "$MODELS_DIR/controlnet/controlnet-flux-canny.safetensors" ]; then
    download_model \
        "https://huggingface.co/InstantX/FLUX.1-dev-ControlNet-Union-alpha/resolve/main/diffusion_pytorch_model.safetensors" \
        "$MODELS_DIR/controlnet/controlnet-flux-canny.safetensors" \
        "ControlNet-Flux-Canny"
fi

# --- AnimateDiff motion modules ---
if [ ! -f "$MODELS_DIR/animatediff/mm_sdxl_v10_beta.ckpt" ]; then
    download_model \
        "https://huggingface.co/guoyww/animatediff/resolve/main/mm_sdxl_v10_beta.ckpt" \
        "$MODELS_DIR/animatediff/mm_sdxl_v10_beta.ckpt" \
        "AnimateDiff SDXL Motion Module"
fi

log ""
log "=== Modelos base listos ==="
log "Checkpoints:  $(ls $MODELS_DIR/checkpoints/ 2>/dev/null | wc -l) archivos"
log "VAEs:         $(ls $MODELS_DIR/vae/ 2>/dev/null | wc -l) archivos"
log "LoRAs:        $(ls $MODELS_DIR/loras/ 2>/dev/null | wc -l) archivos"
log "ControlNet:   $(ls $MODELS_DIR/controlnet/ 2>/dev/null | wc -l) archivos"

log ""
log "Para más modelos, usa ComfyUI-Manager desde http://localhost:8188"
