#!/bin/bash
set -euo pipefail

PACK_PATH="${1:-}"
if [ -z "$PACK_PATH" ]; then
  echo "Uso: $0 <pack-path>"
  exit 1
fi

PACK_NAME=$(basename "$PACK_PATH")
ERRORS=0

echo "🔍 Validando pack: $PACK_NAME"
echo "================================"

# 1. Estructura obligatoria
echo ""
echo "📁 Estructura:"

check_file() {
  if [ -f "$PACK_PATH/$1" ]; then
    echo "  ✅ $1"
  else
    echo "  ❌ $1 (falta)"
    ERRORS=$((ERRORS + 1))
  fi
}

check_dir() {
  if [ -d "$PACK_PATH/$1" ]; then
    echo "  ✅ $1/"
  else
    echo "  ❌ $1/ (falta)"
    ERRORS=$((ERRORS + 1))
  fi
}

check_file "manifest.yaml"
check_dir "skills"
check_dir "agents"
check_dir "prompts"
check_dir "tests"
check_file "README.md"

# 2. YAML válido
echo ""
echo "📄 YAML syntax:"

check_yaml() {
  if python3 -c "import yaml; yaml.safe_load(open('$PACK_PATH/$1'))" 2>/dev/null; then
    echo "  ✅ $1"
  else
    echo "  ❌ $1 (YAML inválido)"
    ERRORS=$((ERRORS + 1))
  fi
}

check_yaml "manifest.yaml"
for f in "$PACK_PATH"/skills/*/skill.yaml; do
  if [ -f "$f" ]; then
    check_yaml "${f#$PACK_PATH/}"
  fi
done
for f in "$PACK_PATH"/agents/*.yaml; do
  if [ -f "$f" ]; then
    check_yaml "${f#$PACK_PATH/}"
  fi
done

# 3. Skills mínimo
echo ""
echo "🧠 Skills:"
SKILL_COUNT=$(ls -d "$PACK_PATH"/skills/*/ 2>/dev/null | wc -l)
if [ "$SKILL_COUNT" -ge 3 ]; then
  echo "  ✅ $SKILL_COUNT skills (mínimo 3)"
else
  echo "  ❌ $SKILL_COUNT skills (necesitas al menos 3)"
  ERRORS=$((ERRORS + 1))
fi

# 4. Agents mínimo
echo ""
echo "🤖 Agents:"
AGENT_COUNT=$(ls "$PACK_PATH"/agents/*.yaml 2>/dev/null | wc -l)
if [ "$AGENT_COUNT" -ge 3 ]; then
  echo "  ✅ $AGENT_COUNT agents (mínimo 3)"
else
  echo "  ❌ $AGENT_COUNT agents (necesitas al menos 3)"
  ERRORS=$((ERRORS + 1))
fi

# 5. Tests Gherkin
echo ""
echo "🧪 Tests:"
GHERKIN_COUNT=$(ls "$PACK_PATH"/tests/features/*.feature 2>/dev/null | wc -l)
if [ "$GHERKIN_COUNT" -ge 1 ]; then
  echo "  ✅ $GHERKIN_COUNT Gherkin features"
else
  echo "  ❌ Sin tests Gherkin"
  ERRORS=$((ERRORS + 1))
fi

# 6. Python syntax check
echo ""
echo "🐍 Python syntax:"
for f in "$PACK_PATH"/skills/*/skill.py; do
  if [ -f "$f" ]; then
    if python3 -m py_compile "$f" 2>/dev/null; then
      echo "  ✅ ${f#$PACK_PATH/}"
    else
      echo "  ❌ ${f#$PACK_PATH/} (error de sintaxis)"
      ERRORS=$((ERRORS + 1))
    fi
  fi
done

echo ""
echo "================================"
if [ $ERRORS -eq 0 ]; then
  echo "✅ Pack válido — listo para deploy"
  exit 0
else
  echo "❌ $ERRORS errores encontrados"
  exit 1
fi
