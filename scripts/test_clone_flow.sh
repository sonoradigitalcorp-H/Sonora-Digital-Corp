#!/usr/bin/env bash
# Test del flujo completo del Clone Service
# Uso: bash test_clone_flow.sh [client_id]

set -euo pipefail
CDIR="/home/mystic/sonora-digital-corp"
CLIENT="${1:-test-$(date +%s)}"
PASS=0
FAIL=0

pass() { PASS=$((PASS+1)); echo "  ✅ $1"; }
fail() { FAIL=$((FAIL+1)); echo "  ❌ $1"; }

echo "=== 🎭 CLONE SERVICE — TEST DE FLUJO COMPLETO ==="
echo "  Cliente: $CLIENT"
echo ""

# 1. Crear pack
echo "[1/5] Creando pack..."
cd "$CDIR"
RESULT=$(PYTHONPATH=. python3 scripts/clone_pipeline.py --client-id "$CLIENT" --action create-pack --pack-type basic 2>&1)
echo "$RESULT" | grep -q "error" && fail "Pack: $RESULT" || pass "Pack basic creado"

# 2. Validar fotos
echo "[2/5] Validando fotos + audio..."
PHOTOS=""
for i in $(seq 1 18); do PHOTOS="$PHOTOS https://storage/photos/$i.jpg"; done
RESULT=$(PYTHONPATH=. python3 scripts/clone_pipeline.py --client-id "$CLIENT" --action validate --photo-urls $PHOTOS --audio-url "https://storage/audio/sample.wav" 2>&1)
echo "$RESULT" | grep -q "ready" && pass "Fotos validadas (18)" || fail "Validación: $RESULT"

# 3. Entrenar
echo "[3/5] Entrenando modelos..."
RESULT=$(PYTHONPATH=. python3 scripts/clone_pipeline.py --client-id "$CLIENT" --action train 2>&1)
echo "$RESULT" | grep -q "trained" && pass "Modelos entrenados" || fail "Entrenamiento: $RESULT"

# 4. Generar assets
echo "[4/5] Generando assets..."
for i in 1 2 3; do
  RESULT=$(PYTHONPATH=. python3 scripts/clone_pipeline.py --client-id "$CLIENT" --action generate --asset-type photo --prompt "oficina ejecutiva $i" 2>&1)
  echo "$RESULT" | grep -q "credits_remaining" && pass "Foto $i generada" || fail "Foto $i: $RESULT"
done
RESULT=$(PYTHONPATH=. python3 scripts/clone_pipeline.py --client-id "$CLIENT" --action generate --asset-type video --prompt "presentación producto" 2>&1)
echo "$RESULT" | grep -q "credits_remaining" && pass "Video generado" || fail "Video: $RESULT"

# 5. Verificar estado final
echo "[5/5] Verificando estado..."
RESULT=$(PYTHONPATH=. python3 scripts/clone_pipeline.py --client-id "$CLIENT" --action status 2>&1)
echo "$RESULT" | grep -q "trained" && pass "Estado: entrenado" || fail "Estado incorrecto"
echo "$RESULT" | python3 -c "import json,sys; d=json.load(sys.stdin); assert d['credits']['photo'] == 7; print('  Créditos restantes:', d['credits'])"

echo ""
echo "=== 📊 RESULTADOS ==="
echo "  ✅ $PASS pasaron"
echo "  ❌ $FAIL fallaron"
echo "  Tests: $(PYTHONPATH=. python3 -m pytest tests/test_clone_*.py -q 2>&1 | tail -1)"
