#!/bin/bash
# Enterprise Score Calculator — Auto-calculates from event data
set -euo pipefail

BASE_DIR="/home/mystic/sonora-digital-corp"
EVENTS="$BASE_DIR/state/logs/events.jsonl"
FIN_OPS="$BASE_DIR/state/finops.jsonl"
SCORE_LOG="$BASE_DIR/state/logs/enterprise-score.log"
mkdir -p "$(dirname "$SCORE_LOG")"

# Score all 10 metrics from 0-10 using event data
python3 - <<PYEOF
import json, sys, os, collections
from datetime import datetime, timedelta

events_path = "${EVENTS}"
finops_path = "${FIN_OPS}"
score_log = "${SCORE_LOG}"

events = []
if os.path.exists(events_path):
    with open(events_path) as f:
        for line in f:
            line = line.strip()
            if line:
                try: events.append(json.loads(line))
                except: pass

finops_calls = []
if os.path.exists(finops_path):
    with open(finops_path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    c = json.loads(line)
                    if c.get("event") == "ai_call": finops_calls.append(c)
                except: pass

now = datetime.utcnow()

# 1. Revenue Impact (0-10) — based on revenue events
revenue_events = [e for e in events if e.get("event") == "revenue_recorded"]
revenue_score = min(10, len(revenue_events)) if revenue_events else 1

# 2. Scalability (0-10) — based on scale events
scale_events = [e for e in events if e.get("event") in ("scaled_up", "scaled_down")]
scalability_score = min(10, len(scale_events) + 3)

# 3. Reusability (0-10) — based on number of OS with skill executions
skill_events = [e for e in events if e.get("event") == "skill_execution"]
os_used = set()
for s in skill_events:
    p = s.get("payload", {})
    if isinstance(p, dict):
        os_used.add(p.get("parent_os", ""))
reusability_score = min(10, len(os_used))

# 4. Automation Impact (0-10) — based on skill executions vs manual events
auto_events = len([e for e in events if e.get("event") == "skill_execution"])
total_ops = len(events)
automation_score = min(10, round(auto_events / max(1, total_ops) * 10)) if total_ops > 0 else 1

# 5. Knowledge Impact (0-10) — based on knowledge_stored events
knowledge_events = [e for e in events if e.get("event") == "knowledge_stored"]
knowledge_score = min(10, len(knowledge_events))

# 6. Reliability (0-10) — based on health events
healthy = len([e for e in events if e.get("event") == "service_healthy"])
down = len([e for e in events if e.get("event") == "service_down"])
total_health = healthy + down
reliability_score = round(healthy / max(1, total_health) * 10) if total_health > 0 else 5

# 7. Founder Independence (0-10) — based on auto-recovery vs manual escalation
recovered = len([e for e in events if e.get("event") == "service_recovered"])
total_incidents = down + recovered
founder_score = min(10, round(recovered / max(1, total_incidents) * 10)) if total_incidents > 0 else 1

# 8. Operational Simplicity (0-10) — fewer event types = simpler
event_types = len(set(e.get("event", "") for e in events))
simplicity_score = max(0, 10 - event_types // 10) if event_types > 0 else 10

# 9. Customer Value (0-10) — based on satisfaction events
satisfaction_events = [e for e in events if e.get("event") == "satisfaction_recorded"]
customer_score = min(10, len(satisfaction_events)) if satisfaction_events else 1

# 10. FinOps Efficiency (0-10) — cost per call
total_cost = sum(c.get("cost", 0) for c in finops_calls)
total_calls = len(finops_calls)
cost_per_call = total_cost / max(1, total_calls)
finops_score = max(0, 10 - round(cost_per_call / 0.001)) if total_calls > 0 else 1

# Calculate total
metrics = {
    "Revenue Impact": revenue_score,
    "Scalability": scalability_score,
    "Reusability": reusability_score,
    "Automation Impact": automation_score,
    "Knowledge Impact": knowledge_score,
    "Reliability": reliability_score,
    "Founder Independence": founder_score,
    "Operational Simplicity": simplicity_score,
    "Customer Value": customer_score,
    "FinOps Efficiency": finops_score,
}

total = sum(metrics.values())

# Log
ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
with open(score_log, "a") as lf:
    lf.write(f"[{ts}] Enterprise Score: {total}/100\n")

print(f"Enterprise Score: {total}/100")
print()
for name, score in metrics.items():
    bar = "█" * score + "░" * (10 - score)
    print(f"  {name:25s} {bar} {score}/10")
print()
print(f"  ─────────────────────────────────────")
print(f"  {'TOTAL':25s} {'█' * (total // 10)}{'░' * (10 - total // 10)} {total}/100")
PYEOF
