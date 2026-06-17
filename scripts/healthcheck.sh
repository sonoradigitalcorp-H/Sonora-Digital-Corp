#!/bin/bash
# Healthcheck diario
ERRORS=0

[ ! -s ~/.config/opencode/opencode.json ] && echo "❌ opencode.json vacío" && ((ERRORS++))
python3 -m json.tool ~/.config/opencode/opencode.json > /dev/null 2>&1 || { echo "❌ opencode.json inválido"; ((ERRORS++)); }
grep -q "sk-" ~/.config/opencode/opencode.json || { echo "❌ No hay API key"; ((ERRORS++)); }

for port in 8000 18789 6333 7687 5678; do
  ss -tlnp | grep -q ":$port " || echo "⚠️ Puerto $port caído"
done

USED=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
[ "$USED" -gt 85 ] && echo "⚠️ Disco al ${USED}%"

echo "✅ Healthcheck completado. Errores: $ERRORS"
exit $ERRORS
