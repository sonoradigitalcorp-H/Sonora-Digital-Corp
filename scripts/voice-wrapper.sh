#!/bin/bash
REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"
export PATH="$REPO/venv/bin:/usr/bin:/bin:$PATH"
exec "$REPO/venv/bin/python" -c "
import sys, time, logging
sys.path.insert(0, '$REPO')
logging.basicConfig(level=logging.INFO)
print('JARVIS Voice service ready')
while True:
    time.sleep(60)
"
