#!/bin/bash
# Weekly Executive Report — corre cada domingo 9 AM
# Genera: reports/WER-YYYYMMDD.json
REPO=/home/ubuntu/sonora-digital-corp
mkdir -p "$REPO/reports"
cd "$REPO" && PYTHONPATH=. python3 scripts/weekly-executive-report.py --json --output "$REPO/reports/"
echo "Weekly report generated: $(date -u)" >> "$REPO/reports/cron.log"
