#!/usr/bin/env python3
"""Monitoreo de contenedores — alerta cuando algo muere.

Uso: python3 scripts/monitor.py              # una vez
     python3 scripts/monitor.py --watch      # cada 60s
"""
import argparse
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("monitor")

BASE = Path(__file__).resolve().parent.parent
EVENTS_FILE = BASE / "state" / "logs" / "events.jsonl"
MEMORY_EVENTS = BASE / "memory" / "learning" / "events.jsonl"


def get_containers() -> list[dict]:
    result = subprocess.run(
        ["docker", "ps", "--format", "{{.Names}}|{{.Status}}|{{.Ports}}"],
        capture_output=True, text=True, timeout=10,
    )
    containers = []
    for line in result.stdout.strip().split("\n"):
        if not line or "|" not in line:
            continue
        parts = line.split("|")
        name = parts[0]
        status = parts[1]
        ports = parts[2] if len(parts) > 2 else ""
        healthy = "healthy" in status or "(healthy)" in status
        running = "Up" in status
        # Containers without healthcheck that are running are considered healthy
        if running and not healthy and "(healthy)" not in status:
            healthy = True  # running without healthcheck = assumed healthy
        containers.append({
            "name": name,
            "status": status,
            "ports": ports,
            "healthy": healthy,
            "running": running,
        })
    return containers


def emit_event(event: dict):
    event["timestamp"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    # State logs
    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EVENTS_FILE, "a") as f:
        f.write(json.dumps(event) + "\n")
    # Memory events
    MEMORY_EVENTS.parent.mkdir(parents=True, exist_ok=True)
    entry = {"event": event.get("type"), "timestamp": event["timestamp"], "payload": event}
    with open(MEMORY_EVENTS, "a") as f:
        f.write(json.dumps(entry) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--watch", action="store_true")
    args = parser.parse_args()

    previous = {}  # name -> healthy

    while True:
        try:
            containers = get_containers()
            all_healthy = all(c["healthy"] for c in containers if c["running"])
            total = len(containers)
            healthy = sum(1 for c in containers if c["healthy"])
            down = [c["name"] for c in containers if c["running"] and not c["healthy"]]
            dead = [c["name"] for c in containers if not c["running"]]

            for c in containers:
                was = previous.get(c["name"], True)
                now = c["healthy"]
                if was and not now:
                    emit_event({
                        "type": "container_down",
                        "container": c["name"],
                        "status": c["status"],
                    })
                    log.warning(f"🔴 {c['name']}: DOWN ({c['status']})")
                elif not was and now:
                    emit_event({
                        "type": "container_recovered",
                        "container": c["name"],
                        "status": c["status"],
                    })
                    log.info(f"🟢 {c['name']}: RECOVERED")
                previous[c["name"]] = now

            status_icon = "✅" if all_healthy else "⚠️"
            log.info(f"{status_icon} Containers: {healthy}/{total} healthy, {len(down)} down, {len(dead)} dead")
            if down:
                for name in down:
                    log.warning(f"  🔴 {name}")
            if dead:
                for name in dead:
                    log.error(f"  💀 {name}")

        except Exception as e:
            log.error(f"Monitor error: {e}")

        if not args.watch:
            break
        time.sleep(60)


if __name__ == "__main__":
    main()
