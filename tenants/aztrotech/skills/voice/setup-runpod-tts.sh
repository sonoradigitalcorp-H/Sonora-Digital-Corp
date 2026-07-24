#!/usr/bin/env bash
# setup-runpod-tts.sh — Deploy Qwen3-TTS como worker serverless en RunPod
# Requisitos: Docker, cuenta RunPod, API key
# Uso: bash setup-runpod-tts.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

echo "=============================="
echo " 🚀 RunPod TTS Worker Setup"
echo "=============================="

# 1. Verificar Docker
if ! command -v docker &>/dev/null; then
    echo "❌ Docker no instalado. Instálalo primero."
    exit 1
fi

# 2. Configurar variables
echo ""
echo "📝 Configura tu cuenta de RunPod:"
read -rp "RunPod API Key: " RUNPOD_API_KEY
read -rp "Nombre de imagen Docker (ej: tuuser/qwen3-tts): " DOCKER_IMAGE

if [ -z "$RUNPOD_API_KEY" ] || [ -z "$DOCKER_IMAGE" ]; then
    echo "❌ Ambos campos son obligatorios"
    exit 1
fi

# 3. Construir imagen
echo ""
echo "🔨 Construyendo imagen Docker..."
cd "$SCRIPT_DIR"

# Copiar archivos de referencia de voz
if [ ! -f "cesar/processed/cesar-ref-short.wav" ]; then
    echo "⚠️  No se encuentra el audio de referencia de César"
    echo "   Asegúrate de que existe en: tenants/aztrotech/skills/voice/cesar/processed/"
    echo "   Continuando sin referencia de voz (usará voz por defecto)..."
fi

docker build -f Dockerfile.runpod -t "$DOCKER_IMAGE" .
echo "✅ Imagen construida: $DOCKER_IMAGE"

# 4. Push a registry
echo ""
echo "📤 Subiendo imagen a Docker Hub..."
docker push "$DOCKER_IMAGE"
echo "✅ Imagen subida"

# 5. Instrucciones para RunPod
echo ""
echo "=============================="
echo " ✅ SETUP COMPLETO"
echo "=============================="
echo ""
echo "Ahora ve a https://www.runpod.io/console/serverless"
echo "y crea un nuevo endpoint con:"
echo ""
echo "  📦 Container: $DOCKER_IMAGE"
echo "  🖥️  GPU: RTX 4090 (recomendada)"
echo "  ⚡ Idle Timeout: 5s (ahorra dinero)"
echo "  🔄 Max Workers: 1 (para empezar)"
echo "  📐 Container Disk: 20GB"
echo ""
echo "Una vez creado, configura las variables de entorno en tu VPS:"
echo ""
echo "  export RUNPOD_API_KEY=$RUNPOD_API_KEY"
echo "  export RUNPOD_TTS_ENDPOINT=<endpoint-id-de-runpod>"
echo "  export GPU_PROVIDER=runpod"
echo ""
echo "O agrégalas a tu ~/.bashrc o al fleet.yml"
echo ""
echo "Para probar:"
echo "  curl -X POST https://api.runpod.ai/v2/<endpoint-id>/runsync \\"
echo "    -H \"Authorization: Bearer $RUNPOD_API_KEY\" \\"
echo "    -H \"Content-Type: application/json\" \\"
echo "    -d '{\"input\": {\"text\": \"Hola, soy Mystic\", \"voice\": \"cesar\"}}'"
echo ""
