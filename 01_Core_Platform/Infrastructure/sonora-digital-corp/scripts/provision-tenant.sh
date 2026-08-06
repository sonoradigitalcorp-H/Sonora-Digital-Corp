#!/bin/bash
set -euo pipefail

# ─────────────────────────────────────────────────────────
# provision-tenant.sh
# Crea un tenant completo desde un pack vertical.
# USO: bash scripts/provision-tenant.sh <pack> <business_name>
# EJ:  bash scripts/provision-tenant.sh joyeria "El Joyero"
# ─────────────────────────────────────────────────────────

PACK="${1:?ERROR: Especifica el pack (ej: joyeria)}"
BUSINESS_NAME="${2:?ERROR: Especifica el nombre del negocio}"
SDC_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# ─── Sanitizar ──────────────────────────────────────────
BUSINESS_SLUG=$(echo "$BUSINESS_NAME" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/-$//')
TENANT_ID="${PACK}_${BUSINESS_SLUG}"

echo "═══ PROVISIONING TENANT ═══"
echo "  Pack:         $PACK"
echo "  Negocio:      $BUSINESS_NAME"
echo "  Tenant ID:    $TENANT_ID"
echo "  Directorio:   $SDC_DIR"
echo ""

# ─── 1. Validar que el pack existe ──────────────────────
PACK_DIR="$SDC_DIR/packs/$PACK"
if [ ! -f "$PACK_DIR/pack.yaml" ]; then
  echo "ERROR: Pack '$PACK' no encontrado en $PACK_DIR"
  exit 1
fi
echo "[1/5] Pack validado ✓"

# ─── 2. Crear entrada en tenants.json ───────────────────
TENANTS_FILE="$SDC_DIR/config/tenants.json"
if [ -f "$TENANTS_FILE" ]; then
  PYTHON_ADD_TENANT=$(cat <<PYEOF
import json, sys
path = "$TENANTS_FILE"
tid = "$TENANT_ID"
name = "$BUSINESS_NAME"
with open(path) as f: data = json.load(f)
data["tenants"][tid] = {
  "name": name,
  "tier": "basic",
  "rate_limit": 50,
  "period_seconds": 60,
  "max_tokens_monthly": 100000,
  "qdrant_collection": "jarvis_knowledge",
  "features": ["chat", "agents", "rag"],
  "status": "active",
  "pack": "$PACK",
  "created": "$(date +%Y-%m-%d)"
}
with open(path, 'w') as f: json.dump(data, f, indent=2)
print(f"Tenant {tid} registrado")
PYEOF
)
  python3 -c "$PYTHON_ADD_TENANT"
  echo "[2/5] Tenant registrado en tenants.json ✓"
else
  echo "  [2/5] SKIP: tenants.json no encontrado ($TENANTS_FILE)"
fi

# ─── 3. Generar opencode.json del cliente ───────────────
CLIENT_DIR="$SDC_DIR/clients/$BUSINESS_SLUG"
mkdir -p "$CLIENT_DIR"

CLIENT_CFG="$CLIENT_DIR/opencode.json"
cat > "$CLIENT_CFG" <<JSONEOF
{
  "\$schema": "https://opencode.ai/config.json",
  "username": "$BUSINESS_NAME — Sonora Digital Corp",
  "model": "opencode/deepseek-v4-flash-free",
  "default_agent": "${PACK}-agent",
  "provider": {
    "openrouter": {
      "name": "OpenRouter Free",
      "options": {
        "baseURL": "https://openrouter.ai/api/v1",
        "apiKey": "\${OPENROUTER_API_KEY}",
        "headers": {
          "HTTP-Referer": "https://sonoradigitalcorp.com",
          "X-Title": "$BUSINESS_NAME"
        }
      },
      "models": {
        "openrouter/free": { "name": "Free Router" },
        "google/gemma-4-31b-it:free": { "name": "Gemma 4 31B" },
        "nvidia/nemotron-3-super-120b-a12b:free": { "name": "Nemotron 3 Super" }
      }
    }
  },
  "instructions": [
    "sonora-enterprise-os/constitution/OMEGA-PROMPT-v10.0.md",
    "config/tenants.json"
  ],
  "agent": {
    "${PACK}-agent": {
      "mode": "primary",
      "model": "opencode/deepseek-v4-flash-free",
      "description": "Agente de $BUSINESS_NAME — asistente personal del negocio",
      "permission": {
        "read": "allow",
        "edit": "ask",
        "bash": "deny",
        "webfetch": "allow",
        "task": "allow"
      }
    },
    "sales-agent": {
      "mode": "subagent",
      "model": "openrouter/google/gemma-4-31b-it:free",
      "description": "Agente de ventas para $BUSINESS_NAME",
      "permission": { "read": "allow", "bash": "deny" }
    }
  }
}
JSONEOF
echo "[3/5] opencode.json generado en $CLIENT_CFG ✓"

# ─── 4. Crear directorio del cliente ────────────────────
mkdir -p "$CLIENT_DIR"/{data,logs,config}
cp "$PACK_DIR/agents/"*.yaml "$CLIENT_DIR/config/" 2>/dev/null || true
cp "$PACK_DIR/skills/"*.yaml "$CLIENT_DIR/config/" 2>/dev/null || true
cp -r "$PACK_DIR/use-cases" "$CLIENT_DIR/" 2>/dev/null || true

echo "[4/5] Directorio cliente creado en $CLIENT_DIR ✓"

# ─── 5. Correr quality gate ─────────────────────────────
echo ""
echo "═══ QUALITY GATE ═══"
if [ -f "$SDC_DIR/scripts/quality-gate.sh" ]; then
  bash "$SDC_DIR/scripts/quality-gate.sh" "$PACK" "$TENANT_ID"
else
  echo "  SKIP: quality-gate.sh no encontrado"
fi

echo ""
echo "═══ PROVISIONING COMPLETO ═══"
echo "  Tenant:    $TENANT_ID"
echo "  Cliente:   $BUSINESS_NAME"
echo "  Config:    $CLIENT_CFG"
echo "  Pack:      $PACK_DIR"
echo "  Para probar: opencode --config $CLIENT_CFG"
echo ""
