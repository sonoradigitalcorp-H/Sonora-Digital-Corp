#!/usr/bin/env bash
# evolution-cron.sh — Trigger Evolution Engine every 6 hours (HAS-008)
# Runs: observe → score → propose → generate
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
LOG="${ROOT}/state/logs/evolution-cron.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] === Evolution Engine Cron ===" | tee -a "$LOG"

# Health check
python3 -m evolution.main --mode check 2>&1 | tee -a "$LOG"

# Propose improvements if score < 70
SCORE=$(python3 -c "import json; print(json.load(open('evolution/scorecard.json')).get('overall', 0))" 2>/dev/null || echo 0)
if [ "$SCORE" -lt 70 ] 2>/dev/null; then
  echo "[$DATE] Score $SCORE < 70. Generating proposals..." | tee -a "$LOG"
  python3 -m evolution.main --mode propose 2>&1 | tee -a "$LOG"
else
  echo "[$DATE] Score $SCORE >= 70. No proposals needed." | tee -a "$LOG"
fi

echo "[$DATE] === Evolution Engine Complete ===" | tee -a "$LOG"
