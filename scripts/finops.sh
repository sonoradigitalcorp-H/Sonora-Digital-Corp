#!/bin/bash
# FinOps — AI Cost Tracking & Budget Manager
# Usage:
#   ./finops.sh log <model> <provider> <input_tokens> <output_tokens> <service>
#   ./finops.sh snapshot [--json|--summary]
#   ./finops.sh daily-report
#   ./finops.sh cost-calc <model> <input_tokens> <output_tokens>

set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FIN_OPS="$BASE_DIR/state/finops.jsonl"
LOG="$BASE_DIR/state/logs/finops.log"

mkdir -p "$(dirname "$LOG")" "$(dirname "$FIN_OPS")"

# ── Pricing Table ($/1K tokens) ──────────────
# Model → input_cost, output_cost per 1K tokens
# Source: official provider pricing (June 2026)
declare -A INPUT_COST
declare -A OUTPUT_COST

INPUT_COST["deepseek-v4-flash-free"]=0
OUTPUT_COST["deepseek-v4-flash-free"]=0

INPUT_COST["deepseek-v3"]=0.0007
OUTPUT_COST["deepseek-v3"]=0.0028

INPUT_COST["deepseek-r1"]=0.00055
OUTPUT_COST["deepseek-r1"]=0.00219

INPUT_COST["gpt-4o"]=0.0025
OUTPUT_COST["gpt-4o"]=0.01

INPUT_COST["gpt-4o-mini"]=0.00015
OUTPUT_COST["gpt-4o-mini"]=0.0006

INPUT_COST["claude-3.5-sonnet"]=0.003
OUTPUT_COST["claude-3.5-sonnet"]=0.015

INPUT_COST["claude-3-haiku"]=0.00025
OUTPUT_COST["claude-3-haiku"]=0.00125

INPUT_COST["gemini-2.0-flash"]=0.0001
OUTPUT_COST["gemini-2.0-flash"]=0.0004

INPUT_COST["gemini-2.0-pro"]=0.002
OUTPUT_COST["gemini-2.0-pro"]=0.005

INPUT_COST["llama-3.1-70b"]=0.00059
OUTPUT_COST["llama-3.1-70b"]=0.00079

INPUT_COST["llama-3.1-8b"]=0.00005
OUTPUT_COST["llama-3.1-8b"]=0.00008

# Default for unknown models
INPUT_COST["default"]=0.001
OUTPUT_COST["default"]=0.002

timestamp() { date -u '+%Y-%m-%dT%H:%M:%SZ'; }

calculate_cost() {
    local model="$1"
    local in_tokens="$2"
    local out_tokens="$3"
    local in_price="${INPUT_COST[$model]:-${INPUT_COST[default]}}"
    local out_price="${OUTPUT_COST[$model]:-${OUTPUT_COST[default]}}"
    local total
    total=$(echo "scale=10; ($in_tokens * $in_price + $out_tokens * $out_price) / 1000" | bc -l 2>/dev/null || echo "0")
    printf "%.10f" "$total" | sed 's/^\./0./' | sed 's/^-\./-0./'
}

# ── Log a call ────────────────────────────────
cmd_log() {
    local model="$1"
    local provider="$2"
    local in_tokens="$3"
    local out_tokens="$4"
    local service="${5:-unknown}"
    local cost
    cost=$(calculate_cost "$model" "$in_tokens" "$out_tokens")
    local ts
    ts=$(timestamp)
    local total=$((in_tokens + out_tokens))
    local entry
    entry=$(cat <<JSON
{"event":"ai_call","timestamp":"${ts}","model":"${model}","provider":"${provider}","service":"${service}","input_tokens":${in_tokens},"output_tokens":${out_tokens},"total_tokens":${total},"cost":${cost}}
JSON
)
    echo "$entry" >> "$FIN_OPS"
    echo "[$ts] 💰 $model → \$${cost} (${in_tokens}i + ${out_tokens}o)" >> "$LOG"
    echo "$cost"
}

# ── Snapshot ──────────────────────────────────
cmd_snapshot() {
    local mode="${1:-summary}"
    if [ ! -f "$FIN_OPS" ] || [ ! -s "$FIN_OPS" ]; then
        echo "{\"total_calls\":0,\"total_cost\":0,\"models\":{}}"
        return
    fi
    python3 - <<PYEOF
import json, sys, collections
mode = "${mode}"
with open("${FIN_OPS}") as f:
    all_lines = [json.loads(l) for l in f if l.strip()]
calls = [c for c in all_lines if c.get("event") == "ai_call"]
total_cost = sum(c.get("cost", 0) for c in calls)
total_tokens = sum(c.get("total_tokens", 0) for c in calls)
models = collections.defaultdict(lambda: {"calls": 0, "cost": 0.0, "tokens": 0})
services = collections.defaultdict(lambda: {"calls": 0, "cost": 0.0})
for c in calls:
    m = c.get("model", "unknown")
    models[m]["calls"] += 1
    models[m]["cost"] += c.get("cost", 0)
    models[m]["tokens"] += c.get("total_tokens", 0)
    s = c.get("service", "unknown")
    services[s]["calls"] += 1
    services[s]["cost"] += c.get("cost", 0)
result = {
    "total_calls": len(calls),
    "total_cost": round(total_cost, 6),
    "total_tokens": total_tokens,
    "models": dict(models),
    "services": dict(services),
    "period": {"from": calls[0]["timestamp"] if calls else "", "to": calls[-1]["timestamp"] if calls else ""}
}
if mode == "--json":
    print(json.dumps(result, indent=2))
else:
    print(f"Calls: {len(calls)} | Cost: \${total_cost:.4f} | Tokens: {total_tokens} | Models: {len(models)}")
PYEOF
}

# ── Daily report ──────────────────────────────
cmd_daily_report() {
    local today
    today=$(date -u '+%Y-%m-%d')
    python3 - <<PYEOF
import json, sys
today = "${today}"
with open("${FIN_OPS}") as f:
    calls = [json.loads(l) for l in f if l.strip()]
today_calls = [c for c in calls if c.get("event") == "ai_call" and c.get("timestamp","").startswith(today)]
total_cost = sum(c.get("cost", 0) for c in today_calls)
total_tokens = sum(c.get("total_tokens", 0) for c in today_calls)
print(f"FinOps Daily — {today}")
print(f"  Calls: {len(today_calls)}")
print(f"  Cost:  \${total_cost:.6f}")
print(f"  Tokens: {total_tokens}")
models = set(c.get("model","") for c in today_calls)
for m in sorted(models):
    mc = [c for c in today_calls if c.get("model") == m]
    mc_cost = sum(c.get("cost",0) for c in mc)
    mc_tok = sum(c.get("total_tokens",0) for c in mc)
    print(f"  {m}: {len(mc)} calls, {mc_tok} tok, \${mc_cost:.6f}")
PYEOF
}

# ── Cost-calc helper ──────────────────────────
cmd_cost_calc() {
    local model="$1"
    local in_tokens="$2"
    local out_tokens="$3"
    local cost
    cost=$(calculate_cost "$model" "$in_tokens" "$out_tokens")
    echo "Model: $model"
    echo "Input:  $in_tokens tokens → \$ $(echo "scale=6; $in_tokens * ${INPUT_COST[$model]:-${INPUT_COST[default]}} / 1000" | bc 2>/dev/null || echo 0)"
    echo "Output: $out_tokens tokens → \$ $(echo "scale=6; $out_tokens * ${OUTPUT_COST[$model]:-${OUTPUT_COST[default]}} / 1000" | bc 2>/dev/null || echo 0)"
    echo "Total:  \$ ${cost}"
}

# ── Baseline entry (first call snapshot) ──────
cmd_baseline() {
    local ts
    ts=$(timestamp)
    local entry
    entry=$(cat <<JSON
{"event":"finops_baseline","timestamp":"${ts}","description":"FinOps initialized","total_historical_cost":0,"tracked_models":["deepseek-v4-flash-free","gpt-4o","gpt-4o-mini","claude-3.5-sonnet","claude-3-haiku","gemini-2.0-flash","gemini-2.0-pro","deepseek-v3","deepseek-r1","llama-3.1-70b","llama-3.1-8b"]}
JSON
)
    echo "$entry" >> "$FIN_OPS"
    echo "[$ts] 📊 FinOps baseline set" >> "$LOG"
    echo "Baseline recorded"
}

# ── Main ──────────────────────────────────────
case "${1:-help}" in
    log)
        shift
        if [ $# -lt 4 ]; then
            echo "Usage: $0 log <model> <provider> <input_tokens> <output_tokens> [service]" >&2
            exit 1
        fi
        cmd_log "$@"
        ;;
    snapshot)
        shift
        cmd_snapshot "${1:---summary}"
        ;;
    daily-report)
        cmd_daily_report
        ;;
    cost-calc)
        shift
        if [ $# -lt 3 ]; then
            echo "Usage: $0 cost-calc <model> <input_tokens> <output_tokens>" >&2
            exit 1
        fi
        cmd_cost_calc "$@"
        ;;
    baseline)
        cmd_baseline
        ;;
    *)
        echo "FinOps — SDC AI Cost Tracking"
        echo ""
        echo "Commands:"
        echo "  log <model> <provider> <in> <out> [svc]  Log an AI call"
        echo "  snapshot [--json]                         Cost summary (all time)"
        echo "  daily-report                              Today's cost breakdown"
        echo "  cost-calc <model> <in> <out>              Estimate call cost"
        echo "  baseline                                  Record initial baseline"
        echo ""
        echo "Example:"
        echo "  $0 log gpt-4o openai 1500 400 chat"
        echo "  $0 snapshot"
        ;;
esac
