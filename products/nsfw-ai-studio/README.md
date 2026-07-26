# 🎬 NSFW AI Studio

Pipeline completo automatizado para generar videos NSFW con IA, entrenar LoRAs, y sincronizar lip-sync.

## Stack

| Servicio | Propósito | Imagen Docker |
|---|---|---|
| **ComfyUI** | Generación img/video con nodos | yanwk/comfyui-boot:cu130-megapak-pt211 |
| **Kohya_SS + AI Toolkit** | Entrenamiento LoRAs | notrius/lora-pilot:stable |
| **AI Toolkit** | Entrenamiento moderno | ostris/aitoolkit:latest |
| **MuseTalk** | Lip-sync | pan93412/musetalk-docker:1.5-gradio |
| **Wav2Lip** | Lip-sync rápido | psyb0t/flickies:latest-cuda |

## Requisitos

- NVIDIA GPU con 24GB+ VRAM (48GB para Flux)
- Docker + docker compose
- NVIDIA Container Toolkit

## Inicio rápido

```bash
# 1. Clonar/entrar al directorio
cd nsfw-ai-studio

# 2. (Opcional) Editar configuración
nano .env

# 3. Descargar modelos base
make setup-models

# 4. Levantar servicios
make up

# 5. Pipeline completo
make auto-pipeline
```

## Comandos

### Gestión del stack
```bash
make up       # Levantar todos los servicios
make down     # Detener servicios
make logs     # Ver logs
make ps       # Estado
make pull     # Actualizar imágenes
```

### Entrenamiento LoRA
```bash
# Entrenar desde línea de comandos
bash scripts/train-lora.sh \
  --name "mi_profesor" \
  --model flux \
  --epochs 20 \
  --rank 32

# Editar config y entrenar
make train-lora CONFIG=configs/lora-training.yaml
```

### Generación de video
```bash
bash scripts/generate-video.sh \
  --workflow configs/workflow-templates/animate-diff.json \
  --prompt "una persona explicando música, primer plano" \
  --lora mi_profesor \
  --frames 49 \
  --steps 30
```

### Lip-sync
```bash
bash scripts/sync-lips.sh \
  --video output/video_generado.mp4 \
  --audio clase_audio.mp3 \
  --tool musetalk
```

### Pipeline completo (todo en uno)
```bash
make auto-pipeline
# Te guía interactivamente por:
# 1. Entrenar LoRA (opcional)
# 2. Generar video
# 3. Sincronizar lip-sync
```

## Estructura de directorios

```
nsfw-ai-studio/
├── docker-compose.yml      # Orquestación
├── Makefile                # Comandos rápidos
├── .env                    # Configuración
├── configs/
│   ├── lora-training.yaml  # Config de entrenamiento
│   └── workflow-templates/ # Workflows ComfyUI
├── datasets/               # Tus imágenes para LoRA
│   └── mi_profesor/
│       ├── img_001.jpg
│       └── img_001.txt     # (caption opcional)
├── models/                 # Modelos descargados
│   ├── checkpoints/
│   ├── loras/              # Tus LoRAS entrenados
│   └── vae/
├── output/                 # Videos y LoRAs generados
├── scripts/                # Automatización
│   ├── setup-models.sh
│   ├── train-lora.sh
│   ├── generate-video.sh
│   ├── sync-lips.sh
│   └── auto-pipeline.sh
└── volumes/                # Datos persistentes
```

## Preparar dataset para LoRA

1. Crea una carpeta en `datasets/` con el nombre del personaje
2. Pon 20-50 fotos (jpg/png), idealmente:
   - 1024x1024 (Flux/SDXL) o 512x512 (SD1.5)
   - Variedad de ángulos, expresiones, fondos
   - Bien iluminadas, rostro visible
3. (Opcional) Agrega un `.txt` por imagen con el caption
4. Ejecuta `bash scripts/train-lora.sh --name nombre`

## Acceso a UIs

| Servicio | URL |
|---|---|
| ComfyUI | http://localhost:8188 |
| Kohya_SS | http://localhost:7860 |
| AI Toolkit | http://localhost:8675 |
| MuseTalk | http://localhost:7861 |
| Wav2Lip | http://localhost:8000 |

## Notas

- NSFW: ComfyUI y estas herramientas NO tienen filtros NSFW incorporados
- VRAM: Flux necesita 48GB+ para training y generación fluida
- Para SDXL puedes usar 24GB sin problemas
