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
    echo "Uso: $0 [opciones]"
    echo ""
    echo "Entrena un LoRA con tus imágenes"
    echo ""
    echo "OPCIONES:"
    echo "  -n, --name NOMBRE       Nombre del LoRA (obligatorio)"
    echo "  -d, --dataset DIR       Directorio con imágenes de entrenamiento"
    echo "  -m, --model MODELO      Modelo base: sd15, sdxl, flux (default: $LORA_BASE_MODEL)"
    echo "  -r, --rank RANK         Rango LoRA (default: $LORA_RANK)"
    echo "  -e, --epochs EPOCHS     Épocas (default: $LORA_EPOCHS)"
    echo "  -l, --lr LR             Learning rate (default: $LORA_LR)"
    echo "  --repeats REPEATS       Repeticiones (default: $LORA_REPEATS)"
    echo "  --resolution RES        Resolución (default: $LORA_RESOLUTION)"
    echo "  -t, --tool TOOL         Trainer: kohya, aitoolkit (default: kohya)"
    echo "  -h, --help              Muestra esta ayuda"
    exit 1
}

# Parse args
NAME=""
DATASET=""
MODEL="${LORA_BASE_MODEL:-flux}"
RANK="${LORA_RANK:-32}"
EPOCHS="${LORA_EPOCHS:-20}"
LR="${LORA_LR:-1e-4}"
REPEATS="${LORA_REPEATS:-20}"
RESOLUTION="${LORA_RESOLUTION:-1024}"
TOOL="kohya"

while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--name)     NAME="$2"; shift 2 ;;
        -d|--dataset)  DATASET="$2"; shift 2 ;;
        -m|--model)    MODEL="$2"; shift 2 ;;
        -r|--rank)     RANK="$2"; shift 2 ;;
        -e|--epochs)   EPOCHS="$2"; shift 2 ;;
        -l|--lr)       LR="$2"; shift 2 ;;
        --repeats)     REPEATS="$2"; shift 2 ;;
        --resolution)  RESOLUTION="$2"; shift 2 ;;
        -t|--tool)     TOOL="$2"; shift 2 ;;
        -h|--help)     usage ;;
        *) error "Argumento desconocido: $1"; usage ;;
    esac
done

if [ -z "$NAME" ]; then
    error "Debes especificar --name NOMBRE"
    usage
fi

# Si no hay dataset, usar el del nombre
if [ -z "$DATASET" ]; then
    DATASET="$PROJECT_DIR/datasets/$NAME"
fi

if [ ! -d "$DATASET" ]; then
    error "Dataset no encontrado: $DATASET"
    info "Crea el directorio y pon tus imágenes allí (jpg/png, mínimo 20)"
    info "  mkdir -p \"$DATASET\""
    exit 1
fi

# Contar imágenes
IMG_COUNT=$(find "$DATASET" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.webp" \) | wc -l)
if [ "$IMG_COUNT" -lt 10 ]; then
    error "Solo $IMG_COUNT imágenes. Necesitas al menos 10-20 para un buen LoRA."
    exit 1
fi

log "========================================="
log "  ENTRENAMIENTO LoRA: $NAME"
log "========================================="
log "Modelo base:    $MODEL"
log "Dataset:        $DATASET ($IMG_COUNT imágenes)"
log "Rango:          $RANK"
log "Épocas:         $EPOCHS"
log "Learning rate:  $LR"
log "Resolución:     $RESOLUTION"
log "Tool:           $TOOL"
log "Output:         $PROJECT_DIR/output/loras/$NAME"
log "========================================="

# Crear output dir
mkdir -p "$PROJECT_DIR/output/loras/$NAME"

case "$TOOL" in
    kohya)
        log "Entrenando con Kohya_SS..."
        docker exec nsfw-kohya bash -c "
            cd /workspace &&
            accelerate launch --num_cpu_threads_per_process 2 \\
                kohya_ss/sdxl_train_network.py \\
                --pretrained_model_name_or_path=models/checkpoints/${MODEL}-base.safetensors \\
                --train_data_dir=datasets/$NAME \\
                --output_dir=output/$NAME \\
                --output_name=$NAME \\
                --network_module=networks.lora \\
                --network_dim=$RANK \\
                --network_alpha=$((RANK/2)) \\
                --learning_rate=$LR \\
                --max_train_steps=$((EPOCHS * IMG_COUNT * REPEATS)) \\
                --train_batch_size=1 \\
                --mixed_precision=fp16 \\
                --save_precision=fp16 \\
                --resolution=$RESOLUTION \\
                --caption_extension=.txt \\
                --cache_latents \\
                --optimizer_type=AdamW8bit \\
                --lr_scheduler=cosine_with_restarts \\
                --lr_warmup_steps=100 \\
                --max_resolution=${RESOLUTION},${RESOLUTION} \\
                --enable_bucket \\
                --min_bucket_res=512 \\
                --max_bucket_res=$RESOLUTION \\
                --seed=42 \\
                --logging_dir=logs/$NAME
        "
        ;;

    aitoolkit)
        log "Entrenando con AI Toolkit..."

        # Generar config YAML temporal
        cat > "$PROJECT_DIR/configs/lora-$NAME.yaml" << YAML
name: $NAME
model:
  base: $MODEL
  path: models/checkpoints/
train:
  batch_size: 1
  epochs: $EPOCHS
  learning_rate: $LR
  resolution: $RESOLUTION
  network:
    type: lora
    rank: $RANK
    alpha: $((RANK/2))
dataset:
  path: datasets/$NAME
  repeats: $REPEATS
output:
  path: output/$NAME
  save_every: 5
YAML

        docker exec nsfw-aitoolkit bash -c "
            cd /app/ai-toolkit &&
            python run.py --config config/lora-$NAME.yaml
        "
        ;;

    *)
        error "Tool desconocida: $TOOL (usa: kohya, aitoolkit)"
        exit 1
        ;;
esac

log "========================================="
log "  LoRA '$NAME' entrenado exitosamente!"
log "  Output: $PROJECT_DIR/output/loras/$NAME"
log "========================================="
log ""
log "Para usarlo en ComfyUI, copia el .safetensors a:"
log "  cp $PROJECT_DIR/output/loras/$NAME/*.safetensors $PROJECT_DIR/models/loras/"
