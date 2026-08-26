#!/usr/bin/env bash
# deploy.sh — Sincroniza código del repo (fuente de verdad) → /opt/hermes/ (producción)
# Uso: ./deploy.sh           # deploy a producción
#      ./deploy.sh --check   # solo diff (no cambia nada)
# El repo vive en /opt/hermes/repo (rama next)
# Mapa: ruta repo canónica → ruta de producción

set -euo pipefail

REPO=/opt/hermes/repo
CHECK="${1:-}"

echo "== Deploy de Sonora Digital Corp =="

# Mapeo de archivos: repo → producción
declare -A MAP=(
  ["01_Core_Platform/04_Automations_and_Workflows/vps_ai_server.py"]="/opt/hermes/vps_ai_server.py"
  ["01_Core_Platform/03_Agentic_Infrastructure/voice/stt_server.py"]="/opt/hermes/voice/stt_server.py"
  ["01_Core_Platform/03_Agentic_Infrastructure/voice/tts_server.py"]="/opt/hermes/voice/tts_server.py"
  ["01_Core_Platform/09_CICD_Pipelines/prompt_registry/run_eval.py"]="/opt/hermes/prompt_registry/run_eval.py"
  ["01_Core_Platform/09_CICD_Pipelines/prompt_registry/eval_prompts.yaml"]="/opt/hermes/prompt_registry/eval_prompts.yaml"
  ["01_Core_Platform/03_Agentic_Infrastructure/wacli_skill.py"]="/opt/hermes/tubandera/wacli_skill.py"
  ["01_Core_Platform/03_Agentic_Infrastructure/sync_metrics.py"]="/opt/hermes/scripts/sync_metrics.py"
  ["01_Core_Platform/03_Agentic_Infrastructure/run_automejora.py"]="/opt/hermes/scripts/run_automejora.py"
  ["02_Client_Projects/Tu_Bandera_Froy/02_Source_Code/personas_db.py"]="/opt/hermes/tubandera/personas_db.py"
  ["02_Client_Projects/Tu_Bandera_Froy/04_Deployment/tubandera.html"]="/var/www/sonoradigitalcorp/tubandera.html"
  ["02_Client_Projects/Hermosillo_Contabilidad/04_Deployment/nathaly.html"]="/var/www/sonoradigitalcorp/nathaly.html"
  ["02_Client_Projects/Sonora_Digital_Corp/04_Deployment/chat_pro_max/index.html"]="/var/www/sonoradigitalcorp/chat.html"
)

for src in "${!MAP[@]}"; do
  dst="${MAP[$src]}"
  if [ ! -f "$REPO/$src" ]; then
    echo "  [SKIP] fuente no existe: $src"
    continue
  fi
  if [ "$CHECK" = "--check" ]; then
    if [ -f "$dst" ] && diff -q "$REPO/$src" "$dst" >/dev/null 2>&1; then
      echo "  [OK] igual: $src"
    else
      echo "  [DIFF] $src"
    fi
  else
    sudo cp "$REPO/$src" "$dst"
    echo "  [DEPLOY] $src → $dst"
  fi
done

if [ "$CHECK" = "--check" ]; then
  echo "== (check) no se cambió nada =="
  exit 0
fi

echo "== Reiniciando servicios afectados =="
sudo systemctl restart vps-ai-server 2>/dev/null && echo "  vps-ai-server: active" || echo "  vps-ai-server: NO reiniciado"
sudo systemctl restart sdc-stt 2>/dev/null && echo "  sdc-stt: active" || echo "  sdc-stt: NO reiniciado"
sudo systemctl restart sdc-tts 2>/dev/null && echo "  sdc-tts: active" || echo "  sdc-tts: NO reiniciado"

echo "== Deploy completo =="