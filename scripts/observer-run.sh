#!/usr/bin/env bash
# observer-run.sh — Collect metrics and update scorecard
cd "$(dirname "$0")/.."
python3 -c "
import sys, json
sys.path.insert(0, '.')
from core.observer import collect
from core.scorecard import calculate as compute_score
metrics = collect()
score = compute_score(metrics)
with open('core/scorecard.json', 'w') as f:
    json.dump({
        'overall': score,
        'metrics': metrics,
        'updated': __import__('datetime').datetime.utcnow().isoformat() + 'Z'
    }, f, indent=2)
print(f'Score: {score} | Agents: {metrics[\"agents\"]} | Caps: {metrics[\"capabilities\"]} | Specs: {metrics[\"specs\"]} | Gherkin: {metrics[\"gherkin_features\"]} | ADRs: {metrics[\"adrs\"]} | Events: {metrics[\"events_count\"]}')
"
