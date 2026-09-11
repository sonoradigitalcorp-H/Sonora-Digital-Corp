#!/usr/bin/env bash
# ==============================================================================
# SCRIPT DE PROVISIONAMIENTO AUTOMÁTICO DE VPS HOSTINGER (45.90.108.12)
# Sonora Digital Corp — Nodo COSUDE / Hermes Architecture
# ==============================================================================

set -e

echo "🚀 Iniciando provisionamiento de VPS HOSTINGER..."

# 1. Actualización del sistema e instalación de dependencias base
echo "📦 Actualizando paquetes de sistema..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl git ufw nginx certbot python3-certbot-nginx python3-pip python3-venv ffmpeg docker.io docker-compose

# 2. Configuración de Firewall (UFW)
echo "🛡️ Configurando Firewall (UFW)..."
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 11434/tcp
sudo ufw --force enable || true

# 3. Habilitar e iniciar Docker
echo "🐳 Configurando Docker..."
sudo systemctl enable --now docker
sudo usermod -aG docker $USER || true

# 4. Desplegar Ollama en Docker (Embeddings y LLM remoto)
echo "🧠 Levantando Ollama (Embeddings)..."
if ! sudo docker ps -a | grep -q ollama; then
    sudo docker run -d --name ollama --restart always -v ollama_data:/root/.ollama -p 11434:11434 ollama/ollama:latest
fi
echo "⏳ Esperando 5s para jalar el modelo all-minilm..."
sleep 5
sudo docker exec -i ollama ollama pull all-minilm || true

# 5. Entorno Python para Webhooks y Servicios Ligeros (Hermosillo Contabilidad, etc.)
echo "🐍 Creando venv para webhooks y servicios..."
mkdir -p /opt/hermes
python3 -m venv /opt/hermes/venv
/opt/hermes/venv/bin/pip install --upgrade pip
/opt/hermes/venv/bin/pip install pydantic requests edge-tts pytz

echo "✅ Provisionamiento base completado en VPS HOSTINGER."
echo "📌 Nota: el stack productivo real se gestiona vía Docker Compose en /opt/sdc/docker-compose.yml."