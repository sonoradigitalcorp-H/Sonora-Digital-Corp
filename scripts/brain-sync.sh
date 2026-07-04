#!/bin/bash
cd /home/ubuntu/sonora-digital-corp
export PYTHONPATH=/home/ubuntu/sonora-digital-corp
LOG="state/logs/brain-sync.log"
echo "[$(date)] Brain sync start" >> "$LOG"
python3 - "$LOG" << 'PYEOF'
import sys
from apps.brain.sync import BrainSyncer
syncer = BrainSyncer()
results = syncer.full_sync()
syncer.close()
log = open(sys.argv[1], 'a')
for name, r in results.items():
    if isinstance(r, dict):
        log.write(f"{name}: {r.get('status')} ({r.get('count', 0)})\n")
log.write(f"Total: {results.get('total_nodes', 0)} nodes\n")
log.close()
PYEOF
echo "[$(date)] Brain sync done" >> "$LOG"
