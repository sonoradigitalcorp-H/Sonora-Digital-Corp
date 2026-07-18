#!/bin/bash
echo "========================================"
echo "  Call Engine — Suite Completa de Tests"
echo "========================================"
echo ""

PASS=0
FAIL=0

run() {
    local name="$1"
    shift
    echo "---------- $name ----------"
    if "$@" 2>&1; then
        echo "✅ $name PASS"
        PASS=$((PASS+1))
    else
        echo "❌ $name FAIL"
        FAIL=$((FAIL+1))
    fi
    echo ""
}

# Nivel 1: Prompt Evals (via Ollama)
run "prompt: call_agent + objection + scoring" python3 scripts/eval_prompts.py
run "prompt: followup" python3 tests/prompts/test_followup.py
run "prompt: summary" python3 tests/prompts/test_summary.py
run "prompt: multi_turn" python3 tests/prompts/test_multi_turn.py

# Nivel 2: Unit Tests
export PATH="/usr/local/go/bin:$PATH"
run "unit: orchestrator" go test ./orchestrator/ -timeout 30s

echo "========================================"
echo "  Resultados: $PASS passed, $FAIL failed"
echo "========================================"
exit $FAIL
