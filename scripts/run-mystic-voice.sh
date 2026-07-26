#!/usr/bin/env bash
# Wrapper para Mystic Voice Realtime (systemd)
set -e

cd /home/ubuntu/sonora-digital-corp
export PYTHONPATH=/home/ubuntu/sonora-digital-corp
export VOICE_PORT=8900
export VOICE_LOG=info

source /tmp/mystic-voice-venv/bin/activate

exec python3 -c "
import sys, os
os.chdir('/home/ubuntu/sonora-digital-corp')
sys.path.insert(0, '/home/ubuntu/sonora-digital-corp')
from apps.voice_realtime.server import app
import uvicorn
uvicorn.run(app, host='127.0.0.1', port=8900, log_level='info')
"
