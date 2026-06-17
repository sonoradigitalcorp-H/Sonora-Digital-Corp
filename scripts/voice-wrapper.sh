#!/bin/bash
cd /home/mystic/sonora-digital-corp
export PATH="/home/mystic/sonora-digital-corp/venv/bin:/usr/bin:/bin:$PATH"
exec /home/mystic/sonora-digital-corp/venv/bin/python -c "
import sys, time, logging
sys.path.insert(0, '/home/mystic/sonora-digital-corp')
logging.basicConfig(level=logging.INFO)
print('JARVIS Voice service ready')
while True:
    time.sleep(60)
"
