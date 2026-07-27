#!/bin/bash
# ═══════════════════════════════════════════════
# Mystic Agent Marketplace — Auto-Provisioning
# ═══════════════════════════════════════════════
# Uso: ./provision.sh --email=ceo@empresa.com --phone=+526621072254 --package=business
# El sistema auto-descubre datos de la empresa y despliega agentes

set -euo pipefail
REPO="$(cd "$(dirname "$0")/../.." && pwd)"

echo "╔═══════════════════════════════════════════════╗"
echo "║   Mystic Agent Marketplace — Provisioning    ║"
echo "╚═══════════════════════════════════════════════╝"

# ─── Parse args ───
for arg in "$@"; do
  case $arg in
    --email=*) EMAIL="${arg#*=}" ;;
    --phone=*) PHONE="${arg#*=}" ;;
    --package=*) PACKAGE="${arg#*=}" ;;
    --business=*) BUSINESS_NAME="${arg#*=}" ;;
    *) echo "❌ Argumento desconocido: $arg"; exit 1 ;;
  esac
done

echo "📧 Email: $EMAIL"
echo "📱 Teléfono: $PHONE"
echo "📦 Paquete: $PACKAGE"

# ─── 1. Auto-descubrimiento del negocio ───
echo ""
echo "🔍 Auto-descubriendo datos del negocio..."

# Extraer dominio del email
DOMAIN=$(echo "$EMAIL" | cut -d@ -f2)
echo "   Dominio detectado: $DOMAIN"

# Intentar resolver datos públicos del dominio
BUSINESS_JSON=$(curl -s "https://api.companydatascore.com/domain/$DOMAIN" 2>/dev/null || echo '{}')
BUSINESS_NAME=$(echo "$BUSINESS_JSON" | grep -o '"name":"[^"]*"' | head -1 | cut -d'"' -f4 || echo "$BUSINESS_NAME")
BUSINESS_NICHE=$(echo "$BUSINESS_JSON" | grep -o '"industry":"[^"]*"' | head -1 | cut -d'"' -f4 || echo "Tecnología")

echo "   Negocio: $BUSINESS_NAME"
echo "   Industria: $BUSINESS_NICHE"

# ─── 2. Crear tenant ───
echo ""
echo "🏗️  Creando tenant..."
TENANT_ID=$(echo "$EMAIL" | md5sum | cut -c1-8)
mkdir -p "$REPO/config/tenants/$TENANT_ID"

cat > "$REPO/config/tenants/$TENANT_ID/tenant.json" << EOF
{
  "id": "$TENANT_ID",
  "email": "$EMAIL",
  "phone": "$PHONE",
  "business_name": "$BUSINESS_NAME",
  "niche": "$BUSINESS_NICHE",
  "package": "$PACKAGE",
  "status": "provisioning",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "agents": []
}
EOF

echo "   Tenant ID: $TENANT_ID"

# ─── 3. Cargar definición del paquete ───
PACKAGE_FILE="$REPO/products/agent-marketplace/packages/$PACKAGE.json"
if [ ! -f "$PACKAGE_FILE" ]; then
  echo "❌ Paquete '$PACKAGE' no encontrado"
  exit 1
fi

AGENTS=$(python3 -c "import json; d=json.load(open('$PACKAGE_FILE')); print(' '.join(d['agents']))")

# ─── 4. Desplegar cada agente ───
echo ""
echo "🤖 Desplegando agentes: $AGENTS"

for AGENT_ID in $AGENTS; do
  echo ""
  echo "  ── $AGENT_ID ──"
  
  AGENT_DIR="$REPO/products/agent-marketplace/agents/$AGENT_ID"
  if [ ! -d "$AGENT_DIR" ]; then
    echo "  ⚠️  Agente '$AGENT_ID' no encontrado, saltando"
    continue
  fi
  
  # Generar env personalizado
  ENV_FILE="$REPO/config/tenants/$TENANT_ID/$AGENT_ID.env"
  if [ -f "$AGENT_DIR/env.template" ]; then
    cp "$AGENT_DIR/env.template" "$ENV_FILE"
    # Poblar variables básicas
    sed -i "s/BUSINESS_NAME=.*/BUSINESS_NAME=$BUSINESS_NAME/" "$ENV_FILE"
    sed -i "s/BUSINESS_NICHE=.*/BUSINESS_NICHE=$BUSINESS_NICHE/" "$ENV_FILE" 2>/dev/null || true
    echo "  ✅ Env generado: $ENV_FILE"
  fi
  
  # Registrar agente en tenant
  python3 -c "
import json
t_path = '$REPO/config/tenants/$TENANT_ID/tenant.json'
t = json.load(open(t_path))
t['agents'].append({
  'id': '$AGENT_ID',
  'status': 'deployed',
  'deployed_at': '$(date -u +%Y-%m-%dT%H:%M:%SZ)',
  'mcp_ready': True
})
json.dump(t, open(t_path, 'w'), indent=2)
print(f'  ✅ Agente $AGENT_ID registrado')
"
done

# ─── 5. Configurar MCP servers ───
echo ""
echo "🔧 Configurando MCP servers..."

MCP_SERVERS=$(python3 -c "import json; d=json.load(open('$PACKAGE_FILE')); print(' '.join(d.get('mcp_servers', [])))")
MCP_CONFIG="$REPO/config/tenants/$TENANT_ID/mcp.json"

echo "{" > "$MCP_CONFIG"
echo '  "tenant_id": "'"$TENANT_ID"'",' >> "$MCP_CONFIG"
echo '  "mcp_servers": [' >> "$MCP_CONFIG"

FIRST=true
for MCP in $MCP_SERVERS; do
  if [ "$FIRST" = true ]; then FIRST=false; else echo "," >> "$MCP_CONFIG"; fi
  echo -n "    {\"name\": \"$MCP\", \"status\": \"ready\"}" >> "$MCP_CONFIG"
done

echo "" >> "$MCP_CONFIG"
echo "  ]" >> "$MCP_CONFIG"
echo "}" >> "$MCP_CONFIG"

echo "   ✅ $MCP_CONFIG configurado"

# ─── 6. Generar dashboard CEO ───
echo ""
echo "📊 Generando dashboard CEO..."

DASHBOARD_DIR="$REPO/products/agent-marketplace/frontend/tenants/$TENANT_ID"
mkdir -p "$DASHBOARD_DIR"

cp "$REPO/products/agent-marketplace/frontend/dashboard.html" "$DASHBOARD_DIR/index.html"
sed -i "s/__TENANT_ID__/$TENANT_ID/g" "$DASHBOARD_DIR/index.html"

echo "   ✅ Dashboard: $DASHBOARD_DIR/index.html"

# ─── 7. Actualizar estado ───
python3 -c "
import json
t_path = '$REPO/config/tenants/$TENANT_ID/tenant.json'
t = json.load(open(t_path))
t['status'] = 'active'
json.dump(t, open(t_path, 'w'), indent=2)
"

echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║   ✅ Provisioning completado                  ║"
echo "║   Tenant: $TENANT_ID                          ║"
echo "║   Email: $EMAIL                               ║"
echo "║   Paquete: $PACKAGE                            ║"
echo "║   Dashboard: http://marketplace/tenant/$TENANT_ID ║"
echo "╚═══════════════════════════════════════════════╝"
