#!/bin/bash
cd /home/mystic/jarvis
export PATH="/home/mystic/jarvis/venv/bin:/usr/bin:/bin:$PATH"
exec /home/mystic/jarvis/venv/bin/python -c "
import sys, time, logging
sys.path.insert(0, '/home/mystic/jarvis')
logging.basicConfig(level=logging.INFO)
print('JARVIS Voice service ready')
while True:
    time.sleep(60)
"
