#!/usr/bin/env python3
"""AgenteMonitor — detecta containers caidos y publica a Redis Stream.

Ciclo: cada 2min verifica Docker → publica container_down a Redis.
Los agentes Healer y Notifier escuchan ese stream.

Uso: python3 apps/agents/monitor_agent.py [--watch]
"""
import argparse
import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "apps" / "jarvis" / "src"))

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("agent.monitor")

REDIS_STREAM = "agent:messages"


def detect_dead_containers() -> list[dict]:
    """Return list of containers that are down or unhealthy."""
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}|{{.Status}}"],
            capture_output=True, text=True, timeout=15,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        log.error(f"Docker error: {e}")
        return []

    down = []
    for line in result.stdout.strip().split("\n"):
        if not line or "|" not in line:
            continue
        name, status = line.split("|", 1)
        is_running = "Up" in status
        is_healthy = "(healthy)" in status or "healthy" in status
        # If running without healthcheck, assume healthy
        if is_running and not is_healthy:
            continue
        if not is_running and not is_healthy:
            down.append({"container": name, "status": status.strip()})
    return down


def publish_to_redis(events: list[dict]) -> int:
    """Publish events to Redis Stream. Returns count of published events."""
    try:
        import redis as redis_lib
        r = redis_lib.Redis(host="localhost", port=6379, db=0, socket_timeout=5, password="sdc2026prod")
        count = 0
        for e in events:
            e["type"] = "container_down"
            e["timestamp"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            e["source"] = "agent.monitor"
            r.xadd(REDIS_STREAM, e, maxlen=1000)
            count += 1
        r.close()
        return count
    except Exception as e:
        log.error(f"Redis error: {e} — falling back to stdout")
        for e in events:
            print(json.dumps(e))
        return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--watch", action="store_true", help="Loop cada 2min")
    args = parser.parse_args()

    while True:
        log.info("Checking containers...")
        down = detect_dead_containers()
        if down:
            published = publish_to_redis(down)
            for d in down:
                log.warning(f"  🔴 {d['container']}: {d['status']} → Redis")
        else:
            log.info("  ✅ All containers healthy")

        if not args.watch:
            break
        time.sleep(120)


if __name__ == "__main__":
    main()
