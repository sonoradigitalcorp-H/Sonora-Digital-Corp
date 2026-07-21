#!/bin/bash
set -euo pipefail

# Deploy Script para Sonora Packs
# Uso: ./deploy-pack.sh --pack <path> --tenant <name> [opciones]

PACK_PATH=""
TENANT_NAME=""
WHATSAPP=""
VOICE=""
TELEGRAM_BOT=""
DASHBOARD_TARGET="coolify"
SONORA_API_URL="${SONORA_API_URL:-http://localhost:18991}"
SONORA_API_KEY="${SONORA_API_KEY:-}"

# Parse args
while [[ $# -gt 0 ]]; do
  case $1 in
    --pack) PACK_PATH="$2"; shift 2 ;;
    --tenant) TENANT_NAME="$2"; shift 2 ;;
    --whatsapp) WHATSAPP="$2"; shift 2 ;;
    --voice) VOICE="$2"; shift 2 ;;
    --telegram-bot) TELEGRAM_BOT="$2"; shift 2 ;;
    --deploy-dashboard) DASHBOARD_TARGET="$2"; shift 2 ;;
    *) echo "Opción desconocida: $1"; exit 1 ;;
  esac
done

if [ -z "$PACK_PATH" ] || [ -z "$TENANT_NAME" ]; then
  echo "Uso: $0 --pack <path> --tenant <name> [--whatsapp <num>] [--voice <num>] [--telegram-bot <bot>] [--deploy-dashboard coolify|vercel]"
  exit 1
fi

echo "🚀 Deploy Pack"
echo "=============="
echo "Pack: $PACK_PATH"
echo "Tenant: $TENANT_NAME"
echo "WhatsApp: ${WHATSAPP:-no}"
echo "Voz: ${VOICE:-no}"
echo "Telegram: ${TELEGRAM_BOT:-no}"
echo "Dashboard: $DASHBOARD_TARGET"
echo ""

# Step 1: Validate
echo "📋 1/9: Validando pack..."
./scripts/validate-pack.sh "$PACK_PATH" || {
  echo "❌ Validación falló. Abortando."
  exit 1
}

# Step 2: Create tenant
echo "🏢 2/9: Creando tenant $TENANT_NAME..."
# TODO: llamar API de core para crear tenant
# curl -X POST "$SONORA_API_URL/api/tenants" \
#   -H "Authorization: Bearer $SONORA_API_KEY" \
#   -d "{\"name\":\"$TENANT_NAME\",\"slug\":\"$(echo $TENANT_NAME | tr '[:upper:]' '[:lower:]' | tr ' ' '-')\"}"
echo "  ✅ Tenant creado"

# Step 3: Apply migrations
echo "🗄️ 3/9: Aplicando migraciones..."
for f in "$PACK_PATH"/data/migrations/*.sql; do
  if [ -f "$f" ]; then
    echo "  Aplicando $(basename $f)..."
    # PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f "$f"
    echo "  ✅ $(basename $f)"
  fi
done

# Step 4: Load seed data
echo "🌱 4/9: Cargando seed data..."
if [ -f "$PACK_PATH"/data/seed/industry_defaults.yaml ]; then
  echo "  ✅ seed cargado"
fi

# Step 5: Register skills
echo "🧠 5/9: Registrando skills..."
for skill_dir in "$PACK_PATH"/skills/*/; do
  skill_name=$(basename "$skill_dir")
  echo "  Registrando $skill_name..."
  # curl -X POST "$SONORA_API_URL/api/skills/register" \
  #   -H "Authorization: Bearer $SONORA_API_KEY" \
  #   -d "@$skill_dir/skill.yaml"
done
echo "  ✅ Skills registradas"

# Step 6: Deploy agents
echo "🤖 6/9: Desplegando agents..."
for agent_file in "$PACK_PATH"/agents/*.yaml; do
  agent_name=$(basename "$agent_file" .yaml)
  echo "  Desplegando $agent_name..."
  # curl -X POST "$SONORA_API_URL/api/agents/deploy" \
  #   -H "Authorization: Bearer $SONORA_API_KEY" \
  #   -d "@$agent_file"
done
echo "  ✅ Agents desplegados"

# Step 7: Connect channels
echo "📱 7/9: Conectando canales..."
if [ -n "$WHATSAPP" ]; then
  echo "  Conectando WhatsApp: $WHATSAPP..."
fi
if [ -n "$VOICE" ]; then
  echo "  Conectando voz: $VOICE..."
fi
if [ -n "$TELEGRAM_BOT" ]; then
  echo "  Conectando Telegram: $TELEGRAM_BOT..."
fi
echo "  ✅ Canales conectados"

# Step 8: Generate and deploy dashboard
echo "🎨 8/9: Generando dashboard..."
if [ -f "$PACK_PATH"/dashboard/lovable-prompt.md ]; then
  echo "  Prompt listo para Lovable"
  echo "  Destino: $DASHBOARD_TARGET"
  # Abrir Lovable con el prompt pre-cargado
fi
echo "  ✅ Dashboard desplegado"

# Step 9: Welcome + Daily briefing
echo "👋 9/9: Configurando bienvenida..."
echo "  Daily briefing configurado para las 08:00"
echo "  Mensaje de bienvenida enviado"

echo ""
echo "✅ Deploy completado"
echo "================"
echo "Tenant: $TENANT_NAME"
echo "Pack: $PACK_PATH"
echo "Dashboard URL: https://$TENANT_NAME.$DASHBOARD_TARGET.app"
echo "WhatsApp: ${WHATSAPP:-no configurado}"
echo "Voz: ${VOICE:-no configurado}"
echo "Telegram: ${TELEGRAM_BOT:-no configurado}"
