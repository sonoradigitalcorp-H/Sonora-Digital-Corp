#!/bin/bash
# Resumen rápido al iniciar una sesión
# Dice: dónde estoy, en qué branch, qué cambió, qué hay pendiente

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)" || exit 1
cd "$ROOT" || exit 1

echo "╔══════════════════════════════════════╗"
echo "║     SONORA DIGITAL CORP             ║"
echo "║     Resumen de sesión               ║"
echo "╚══════════════════════════════════════╝"
echo ""

# 1. Carpeta actual
echo "📍 Carpeta: $ROOT"

# 2. Rama actual
BRANCH=$(git branch --show-current)
echo "🌿 Rama: $BRANCH"

# 3. Rama main vs actual
  git fetch origin main 2>/dev/null || true
  AHEAD=$(git rev-list --count origin/main..."$BRANCH" 2>/dev/null || echo 0)
  BEHIND=$(git rev-list --count "$BRANCH"...origin/main 2>/dev/null || echo 0) || true
if [ "$AHEAD" -gt 0 ] || [ "$BEHIND" -gt 0 ]; then
  echo "⚠️  Diferencia con main: +$AHEAD adelante | -$BEHIND atrás"
  if [ "$BEHIND" -gt 0 ]; then
    echo "   → main tiene commits que esta rama NO tiene"
    echo "   → Sugerencia: git merge origin/main"
  fi
else
  echo "✅ Al día con main"
fi

# 4. Cambios sin commit
DIRTY=$(git status --porcelain | wc -l)
if [ "$DIRTY" -gt 0 ]; then
  echo "📝 Archivos sin commit: $DIRTY"
  git status --short | head -10
else
  echo "✅ Sin cambios pendientes"
fi

# 5. Últimos commits
echo ""
echo "═══ Últimos commits ═══"
git log --oneline -5

# 6. Otras ramas con actividad reciente (otros sessions)
echo ""
echo "═══ Otras ramas activas ═══"
BRANCHES=$(git branch -r --sort=-committerdate 2>/dev/null | head -10 || true)
while read -r r; do
  [ -z "$r" ] && continue
  rname=$(echo "$r" | sed 's/.*\///')
  if [ "$rname" != "main" ] && [ "$rname" != "HEAD" ] && [ "$rname" != "$BRANCH" ]; then
    last=$(git log --oneline "origin/$rname" -1 2>/dev/null | head -1)
    echo "  $rname → $last"
  fi
done <<< "$BRANCHES"

# 7. Memoria de la sesión anterior
echo ""
echo "═══ Última sesión ═══"
if [ -f "$ROOT/state/ultima-sesion.json" ]; then
  python3 -c "
import json
with open('$ROOT/state/ultima-sesion.json') as f:
    d = json.load(f)
print(f\"  Branch: {d.get('branch','?')}\")
print(f\"  Resumen: {d.get('resumen','?')}\")
print(f\"  Fecha: {d.get('fecha','?')}\")
" 2>/dev/null || echo "  (no se pudo leer)"
else
  echo "  (es la primera sesión o no se guardó resumen)"
fi

# 8. Lecciones aprendidas (correcciones del usuario)
echo ""
echo "═══ Reglas aprendidas ═══"
if [ -f "$ROOT/memory/sdc-rules.md" ]; then
  head -5 "$ROOT/memory/sdc-rules.md"
else
  echo "  (aún no hay reglas aprendidas)"
fi

echo ""
echo "💡 ¿Qué necesitas?"
