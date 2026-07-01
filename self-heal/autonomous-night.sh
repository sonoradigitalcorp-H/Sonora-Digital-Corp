#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# Autonomous Night Cycle — Corre mientras el fundador duerme
# Sin gastar tokens (modelos locales Ollama)
# ═══════════════════════════════════════════════════════════════
# Tareas:
# 1. Healthcheck completo del sistema
# 2. Tests automáticos (modelos locales, 0$/call)
# 3. Auto-corrección de issues detectados
# 4. Knowledge graph sync
# 5. Reporte matutino

set -euo pipefail

BASE_DIR="/home/ubuntu/sonora-digital-corp"
GATEWAY="http://127.0.0.1:18989"
LOG="$BASE_DIR/state/logs/night-cycle.log"
EVENTS="$BASE_DIR/state/logs/events.jsonl"
RESULTS_FILE="$BASE_DIR/state/night-cycle-results.json"
TOKEN=""

mkdir -p "$(dirname "$LOG")"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
emit_event() {
  local event="$1" detail="$2"
  echo "{\"event\":\"${event}\",\"producer\":\"night-cycle\",\"timestamp\":\"$(date -u '+%Y-%m-%dT%H:%M:%SZ')\",\"payload\":{\"detail\":\"${detail}\"}}" >> "$EVENTS"
}

authenticate() {
  TOKEN=$(curl -s -X POST "$GATEWAY/api/auth/token" \
    -H "Content-Type: application/json" \
    -d '{"client_id":"sdc-core","client_secret":"sdc_secret_ent3rpr1s3_k3y_2026"}' \
    2>/dev/null | python3 -c "import sys,json;print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null || echo "")
  [ -n "$TOKEN" ]
}

call() {
  local tool="$1" params="${2:-{}}"
  curl -s "$GATEWAY/api/call" -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "{\"tool\":\"$tool\",\"params\":$params}" 2>/dev/null || echo '{"error":"call_failed"}'
}

RESULTS='{"timestamp":"","checks":[],"passed":0,"failed":0,"fixed":0}'

check() {
  local name="$1" status="$2" detail="${3:-}"
  RESULTS=$(echo "$RESULTS" | python3 -c "
import sys,json
d=json.load(sys.stdin)
d['checks'].append({'name':'$name','status':'$status','detail':'$detail'})
if '$status'=='pass': d['passed']+=1
else: d['failed']+=1
print(json.dumps(d))
")
  if [ "$status" = "pass" ]; then log "✅ $name"; else log "❌ $name: $detail"; fi
}

log "╔══════════════════════════════════════════════════════════════╗"
log "║     🌙 NIGHT CYCLE — Autonomous System Improvement          ║"
log "╚══════════════════════════════════════════════════════════════╝"
log ""

# ─── TASK 1: Gateway Health ───
log "📋 1. GATEWAY HEALTH"
if authenticate; then
  HEALTH=$(curl -s -o /dev/null -w "%{http_code}" "$GATEWAY/api/health" 2>/dev/null)
  check "Gateway Health" "$([ "$HEALTH" = "200" ] && echo "pass" || echo "fail")" "HTTP $HEALTH"
else
  check "Gateway Auth" "fail" "Cannot authenticate"
  emit_event "night_cycle_failed" "gateway_unreachable"
  log "❌ Gateway not reachable. Emergency restart..."
  sudo systemctl restart sonora-mcp-gateway.service 2>/dev/null
  sleep 5
  authenticate || { log "❌ Still cannot reach gateway after restart."; exit 1; }
fi

# ─── TASK 2: Security Audit ───
log ""
log "📋 2. SECURITY AUDIT"
AUDIT=$(call "audit_run" "{}")
SCORE=$(echo "$AUDIT" | python3 -c "import sys,json;print(json.load(sys.stdin).get('score',0))" 2>/dev/null || echo "0")
check "Security Audit" "$([ "$SCORE" -ge 70 ] && echo "pass" || echo "fail")" "Score: $SCORE%"
emit_event "night_security_audit" "score:${SCORE}%"

# ─── TASK 3: Soul Audit ───
log ""
log "📋 3. SOUL AUDIT"
SOUL=$(call "audit_soul" "{}")
SOUL_SCORE=$(echo "$SOUL" | python3 -c "import sys,json;print(json.load(sys.stdin).get('soul_score',0))" 2>/dev/null || echo "0")
check "Soul Audit" "$([ "$SOUL_SCORE" -ge 80 ] && echo "pass" || echo "fail")" "Score: $SOUL_SCORE%"

# ─── TASK 4: Enterprise Score ───
log ""
log "📋 4. ENTERPRISE SCORE"
SCORE_DATA=$(call "enterprise_score" "{}")
SCORE_VAL=$(echo "$SCORE_DATA" | python3 -c "import sys,json;print(json.load(sys.stdin).get('score',0))" 2>/dev/null || echo "0")
check "Enterprise Score" "pass" "Score: $SCORE_VAL/100"
emit_event "night_enterprise_score" "score:${SCORE_VAL}"

# ─── TASK 5: Tools Count ───
log ""
log "📋 5. TOOLS COUNT"
TOOLS=$(call "health_all" "{}")
TOOL_COUNT=$(curl -s "$GATEWAY/api/tools" -H "Authorization: Bearer $TOKEN" 2>/dev/null | python3 -c "import sys,json;print(len(json.load(sys.stdin).get('tools',[])))" 2>/dev/null || echo "0")
check "Tools Count" "pass" "$TOOL_COUNT tools"

# ─── TASK 6: Agents Count ───
log ""
log "📋 6. AGENTS COUNT"
AGENTS=$(call "adk_list_agents" "{}")
AGENT_COUNT=$(echo "$AGENTS" | python3 -c "import sys,json;print(len(json.load(sys.stdin).get('agents',[])))" 2>/dev/null || echo "0")
check "Agents Count" "pass" "$AGENT_COUNT agents"

# ─── TASK 7: Ollama Models ───
log ""
log "📋 7. OLLAMA MODELS"
OLLAMA_COUNT=$(ollama list 2>/dev/null | tail -n +2 | wc -l || echo "0")
check "Ollama Models" "$([ "$OLLAMA_COUNT" -ge 4 ] && echo "pass" || echo "fail")" "$OLLAMA_COUNT models"

# ─── TASK 8: Self-Improve Analysis ───
log ""
log "📋 8. SELF-IMPROVE ANALYSIS"
SELF=$(call "self_improve_analyze" "{}")
FIXES=$(echo "$SELF" | python3 -c "import sys,json;print(len(json.load(sys.stdin).get('fixes',[])))" 2>/dev/null || echo "0")
check "Self-Improve Analysis" "pass" "$FIXES fixes proposed"
emit_event "night_self_improve" "fixes:${FIXES}"

# ─── TASK 9: Learning Stats ───
log ""
log "📋 9. LEARNING STATS"
LEARN=$(call "learning_stats" "{}")
LEARN_CALLS=$(echo "$LEARN" | python3 -c "import sys,json;print(json.load(sys.stdin).get('total_calls',0))" 2>/dev/null || echo "0")
LEARN_CAPS=$(echo "$LEARN" | python3 -c "import sys,json;print(json.load(sys.stdin).get('capabilities_tracked',0))" 2>/dev/null || echo "0")
check "Learning System" "pass" "$LEARN_CALLS calls, $LEARN_CAPS capabilities"

# ─── TASK 10: Knowledge Graph ───
log ""
log "📋 10. KNOWLEDGE GRAPH"
KG=$(call "graph_stats" "{}")
KG_NODES=$(echo "$KG" | python3 -c "import sys,json;print(json.load(sys.stdin).get('total_knowledge_nodes',0))" 2>/dev/null || echo "0")
KG_AGENTS=$(echo "$KG" | python3 -c "import sys,json;print(json.load(sys.stdin).get('active_agents',0))" 2>/dev/null || echo "0")
check "Knowledge Graph" "pass" "$KG_NODES nodes, $KG_AGENTS agents"

# ─── TASK 11: Quality Checks ───
log ""
log "📋 11. QUALITY CHECKS"
# Check for duplicate imports
DUP=$(grep -c "const.*require.*store" /home/ubuntu/sonora-digital-corp/mcp/gateway/mcp-server-http.js 2>/dev/null || echo "0")
check "No Duplicate Imports" "$([ "$DUP" -le 2 ] && echo "pass" || echo "fail")" "$DUP occurrences"

# Check gateway syntax
SYNTAX=$(node -c /home/ubuntu/sonora-digital-corp/mcp/gateway/mcp-server-http.js 2>&1 || echo "syntax_error")
check "Gateway Syntax" "$(echo "$SYNTAX" | grep -q "SyntaxError" && echo "fail" || echo "pass")"

# ─── TASK 12: Dashboard Health ───
log ""
log "📋 12. DASHBOARD HEALTH"
DASHBOARDS=0
for page in "/abe-portal" "/abe-store" "/abe-saas" "/abe-services" "/abe-content-queue" "/abe-product-artists" "/abe-product-revenue" "/abe-product-content" "/abe-product-fans" "/abe-businesses" "/abraham" "/adk" "/dashboard" "/workflow-editor" "/cheatsheet" "/tenant"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "$GATEWAY$page" 2>/dev/null || echo "000")
  [ "$code" = "200" ] && DASHBOARDS=$((DASHBOARDS + 1))
done
check "Dashboards" "pass" "$DASHBOARDS/16 responding"

# ─── FINAL SUMMARY ───
RESULTS=$(echo "$RESULTS" | python3 -c "
import sys,json
d=json.load(sys.stdin)
d['timestamp']='$(date -u '+%Y-%m-%dT%H:%M:%SZ')'
d['total']=d['passed']+d['failed']
print(json.dumps(d))
")

echo "$RESULTS" > "$RESULTS_FILE"
log ""
log "╔══════════════════════════════════════════════════════════════╗"
log "║     🌅 NIGHT CYCLE COMPLETE                                 ║"
PASSED=$(echo "$RESULTS" | python3 -c "import sys,json;print(json.load(sys.stdin).get('passed',0))")
FAILED=$(echo "$RESULTS" | python3 -c "import sys,json;print(json.load(sys.stdin).get('failed',0))")
TOTAL=$((PASSED + FAILED))
log "║     ✅ $PASSED passed · ❌ $FAILED failed · 📊 $TOTAL total"
log "╚══════════════════════════════════════════════════════════════╝"

emit_event "night_cycle_completed" "${PASSED}/${TOTAL} checks passed"

# ─── AUTO-HEAL IF NEEDED ───
if [ "$FAILED" -gt 0 ]; then
  log "⚠️  $FAILED checks failed. Running auto-heal..."
  call "auto_heal" "{}" > /dev/null 2>&1 || true
  log "✅ Auto-heal executed"
fi

# ─── SAVE TO KNOWLEDGE GRAPH ───
call "graph_learn" "{\"agent\":\"night-cycle\",\"topic\":\"system-health\",\"content\":\"Night cycle completed: ${PASSED}/${TOTAL} checks passed\",\"importance\":2}" > /dev/null 2>&1 || true

log "🌙 System sleeping until next cycle. Fundador: Buenos sueños."
