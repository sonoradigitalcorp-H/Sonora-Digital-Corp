#!/usr/bin/env python3
"""Simple WebSocket server that broadcasts new events to the Command Center dashboard.

Usage:
    python3 products/command-center/events.py

Listens on ws://localhost:8767.
Watches state/events/events.jsonl for changes and pushes new lines to all connected clients.
"""

import asyncio
import json
import os
import time
from pathlib import Path

import websockets

EVENTS_PATH = Path(__file__).resolve().parent.parent.parent / "state" / "events" / "events.jsonl"
HOST = "0.0.0.0"
PORT = 8767

connected = set()


async def broadcast(message):
    if not connected:
        return
    msg = json.dumps(message)
    await asyncio.gather(
        *(client.send(msg) for client in connected.copy()),
        return_exceptions=True,
    )


async def handler(websocket):
    connected.add(websocket)
    try:
        async for _ in websocket:
            pass
    finally:
        connected.discard(websocket)


async def watcher():
    """Poll events.jsonl every 2s and push new lines."""
    last_size = 0
    if EVENTS_PATH.exists():
        last_size = EVENTS_PATH.stat().st_size

    while True:
        await asyncio.sleep(2)
        if not EVENTS_PATH.exists():
            continue
        try:
            current_size = EVENTS_PATH.stat().st_size
            if current_size > last_size:
                with open(EVENTS_PATH) as f:
                    f.seek(last_size)
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                event = json.loads(line)
                                await broadcast({
                                    "type": "new_event",
                                    "event": event,
                                    "timestamp": time.time(),
                                })
                            except json.JSONDecodeError:
                                pass
                last_size = current_size
        except OSError:
            pass


async def main():
    print(f"⚡ Events WebSocket server: ws://{HOST}:{PORT}")
    print(f"   Watching: {EVENTS_PATH}")
    async with websockets.serve(handler, HOST, PORT):
        await watcher()


if __name__ == "__main__":
    asyncio.run(main())
