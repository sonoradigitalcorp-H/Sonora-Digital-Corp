#!/bin/bash
# Healthcheck diario — Native Agent OS
ERRORS=0
WARN=0

echo "🔍 SDC Healthcheck — Native Agent OS"
echo "====================================="

# ── MCP Gateway (entry point) ──
MCP_CODE=$(curl -so /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:18989/api/health 2>/dev/null || echo "000")
if [ "$MCP_CODE" = "200" ]; then
  echo "✅ MCP Gateway: UP (:18989)"
else
  echo "❌ MCP Gateway: DOWN (:18989)"
  ((ERRORS++))
fi

# ── Capability Registry ──
TOKEN=$(curl -s -X POST http://127.0.0.1:18989/api/auth/token \
  -H 'Content-Type: application/json' \
  -d "{\"client_id\":\"sdc-core\",\"client_secret\":\"${SONORA_CLIENT_SECRET:-sdc_secret_ent3rpr1s3_k3y_2026}\"}" 2>/dev/null | \
  python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null || echo "")
if [ -n "$TOKEN" ]; then
  CAPS=$(curl -s http://127.0.0.1:18989/api/capability/list -H "Authorization: Bearer $TOKEN" 2>/dev/null | \
    python3 -c "import sys,json; print(len(json.load(sys.stdin).get('capabilities',[])))" 2>/dev/null || echo "0")
  echo "✅ Capability Registry: $CAPS capabilities"
else
  echo "⚠️ Capability Registry: auth not tested"
  ((WARN++))
fi

# ── Servicios Docker ──
for port in 8000 18789 6333 7687 5678 5432 6379; do
  ss -tlnp 2>/dev/null | grep -q ":$port " || echo "⚠️ Puerto $port caído (Docker)"
done

# ── Disco ──
USED=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$USED" -gt 85 ]; then
  echo "⚠️ Disco al ${USED}%"
  ((WARN++))
else
  echo "✅ Disco: ${USED}%"
fi

# ── opencode config ──
if [ -s ~/.config/opencode/opencode.json ]; then
  echo "✅ opencode.json: OK"
else
  echo "⚠️ opencode.json: vacío o no encontrado"
  ((WARN++))
fi

echo ""
echo "📊 Resumen: $ERRORS errores, $WARN advertencias"
exit $ERRORS
