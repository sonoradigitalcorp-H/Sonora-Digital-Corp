#!/usr/bin/env bash
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR/../.."

echo "[ABE Service] Installing deps..."
pip install -q -r "$DIR/requirements.txt"

echo "[ABE Service] Starting on 127.0.0.1:5180..."
exec python3 -m uvicorn apps.abe-service.main:app \
  --host 127.0.0.1 \
  --port 5180 \
  --reload \
  --log-level info
