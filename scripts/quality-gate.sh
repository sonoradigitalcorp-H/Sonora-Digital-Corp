#!/bin/bash
set -euo pipefail

# ─────────────────────────────────────────────────────────
# quality-gate.sh
# Evalúa la calidad de un pack: tests, estructura, métricas
# USO: bash scripts/quality-gate.sh <pack> [tenant_id]
# ─────────────────────────────────────────────────────────

PACK="${1:?ERROR: Especifica el pack (ej: joyeria)}"
TENANT_ID="${2:-test}"
SDC_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PACK_DIR="$SDC_DIR/packs/$PACK"

echo ""
echo "═══ QUALITY GATE: $PACK ═══"
PASS=0
FAIL=0
TOTAL=0

check() {
  TOTAL=$((TOTAL + 1))
  local desc="$1"
  local result="$2"
  if [ "$result" = "ok" ]; then
    PASS=$((PASS + 1))
    echo "  ✅ $desc"
  else
    FAIL=$((FAIL + 1))
    echo "  ❌ $desc — $result"
  fi
}

# ─── 1. Verificar estructura del pack ───────────────────
echo ""
echo "── Estructura ──"

check "pack.yaml existe" "$([ -f "$PACK_DIR/pack.yaml" ] && echo "ok" || echo "no encontrado")"
check "directorio agents/" "$([ -d "$PACK_DIR/agents" ] && echo "ok" || echo "no existe")"
check "directorio skills/" "$([ -d "$PACK_DIR/skills" ] && echo "ok" || echo "no existe")"
check "directorio use-cases/" "$([ -d "$PACK_DIR/use-cases" ] && echo "ok" || echo "no existe")"
check "directorio tests/" "$([ -d "$PACK_DIR/tests" ] && echo "ok" || echo "no existe")"

# ─── 2. Validar YAMLs ───────────────────────────────────
echo ""
echo "── YAMLs ──"

for yaml_file in "$PACK_DIR/pack.yaml" "$PACK_DIR/agents/"*.yaml "$PACK_DIR/skills/"*.yaml; do
  [ -f "$yaml_file" ] || continue
  name=$(basename "$yaml_file")
  if python3 -c "import yaml; yaml.safe_load(open('$yaml_file'))" 2>/dev/null; then
    check "YAML válido: $name" "ok"
  else
    check "YAML válido: $name" "error sintáctico"
  fi
done

# ─── 3. Verificar pack.yaml contra archivos ─────────────
echo ""
echo "── Consistencia ──"

if [ -f "$PACK_DIR/pack.yaml" ]; then
  AGENTS=$(python3 -c "import yaml; d=yaml.safe_load(open('$PACK_DIR/pack.yaml')); print(' '.join(d.get('agents',[])))" 2>/dev/null || echo "")
  for agent in $AGENTS; do
    check "Agente YAML: $agent" "$([ -f "$PACK_DIR/agents/$agent.yaml" ] && echo "ok" || echo "falta $agent.yaml")"
  done

  SKILLS=$(python3 -c "import yaml; d=yaml.safe_load(open('$PACK_DIR/pack.yaml')); print(' '.join(d.get('skills',[])))" 2>/dev/null || echo "")
  for skill_ref in $SKILLS; do
    skill_name=$(echo "$skill_ref" | cut -d/ -f2)
    check "Skill YAML: $skill_name" "$([ -f "$PACK_DIR/skills/$skill_name.yaml" ] && echo "ok" || echo "falta $skill_name.yaml")"
  done
fi

# ─── 4. Correr tests ────────────────────────────────────
echo ""
echo "── Tests ──"

if [ -d "$PACK_DIR/tests" ]; then
  cd "$SDC_DIR"
  if python3 -m pytest "$PACK_DIR/tests" -q --tb=short 2>&1; then
    check "Tests del pack" "ok"
  else
    check "Tests del pack" "FAIL"
  fi
else
  check "Tests del pack" "no hay directorio tests/"
fi

# ─── 5. Validar Gherkin ─────────────────────────────────
echo ""
echo "── Gherkin ──"

eval "$(python3 - "$PACK_DIR" <<'PYEOF'
import sys, glob, os
pack_dir = sys.argv[1]
uc_dir = os.path.join(pack_dir, "use-cases")
lines = []
for f in sorted(glob.glob(os.path.join(uc_dir, "*.feature"))):
    name = os.path.basename(f)
    with open(f) as fh:
        content = fh.read()
    has_f = "Feature:" in content
    has_s = "Scenario:" in content
    if has_f and has_s:
        sc = content.count("Scenario:")
        lines.append(f'check "Gherkin válido: {name} ({sc} scenarios)" "ok"')
    elif not has_f:
        lines.append(f'check "Gherkin válido: {name}" "sin Feature"')
    else:
        lines.append(f'check "Gherkin válido: {name}" "sin Scenario"')
print("; ".join(lines))
PYEOF
)"

# ─── Resumen ────────────────────────────────────────────
echo ""
echo "═══ RESULTADO ═══"
SCORE=$((PASS * 100 / TOTAL))
echo "  $PASS/$TOTAL pruebas pasaron ($SCORE%)"

if [ "$SCORE" -ge 80 ]; then
  echo "  ✅ QUALITY GATE: APROBADO"
elif [ "$SCORE" -ge 60 ]; then
  echo "  ⚠️  QUALITY GATE: ACEPTABLE (revisa fallos)"
else
  echo "  ❌ QUALITY GATE: REPROBADO"
fi

echo ""

# ─── Guardar resultado ──────────────────────────────────
RESULTS_DIR="$SDC_DIR/packs/$PACK/metrics"
mkdir -p "$RESULTS_DIR"
cat > "$RESULTS_DIR/last-gate.json" <<JSONEOF
{
  "pack": "$PACK",
  "tenant": "$TENANT_ID",
  "date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "passed": $PASS,
  "total": $TOTAL,
  "score": $SCORE,
  "threshold": 80,
  "status": "$([ "$SCORE" -ge 80 ] && echo 'approved' || ([ "$SCORE" -ge 60 ] && echo 'warning' || echo 'failed'))"
}
JSONEOF

exit $([ "$SCORE" -ge 60 ] && echo 0 || echo 1)
