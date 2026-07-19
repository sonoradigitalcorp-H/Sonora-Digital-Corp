"""Ops Agent — Monitor de servicios.
Checkea servicios cada N segundos, emite eventos al bus.
Usage: python -m ops.monitor [--interval 300] [--once]
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
STATE_FILE = BASE / "state" / "ops" / "service-state.json"

SERVICES = [
    ("hermes", "docker"),
    ("hermes-dashboard", "docker"),
    ("sdc-neo4j", "docker"),
    ("supabase-kong", "docker"),
    ("supabase-db", "docker"),
    ("supabase-studio", "docker"),
    ("sdc-redis", "docker"),
    ("sdc-qdrant", "docker"),
    ("sdc-grafana", "docker"),
    ("sonora-hasura", "docker"),
    ("sdc-pgadmin4", "docker"),
    ("sdc-omnivoice", "docker"),
    ("syncthing@ubuntu", "systemd"),
    ("event-listener", "systemd"),
    ("omnivoice-agent", "systemd"),
]


def emit(event_type: str, payload: dict):
    """Emit event via file + Supabase + RabbitMQ."""
    try:
        from events.emitter import emit_sync
        emit_sync(event_type, payload, "ops-agent")
    except ImportError:
        pass

    try:
        from ops.supabase_emitter import emit_to_supabase, emit_to_rabbitmq
        severity = "critical" if "down" in event_type else "warning" if "warning" in event_type else "info"
        emit_to_supabase(event_type, payload, severity)
        emit_to_rabbitmq(event_type, payload)
    except Exception:
        pass


def check_docker(name: str) -> str:
    result = subprocess.run(
        ["docker", "inspect", name, "--format", "{{.State.Status}}"],
        capture_output=True, text=True, timeout=10,
    )
    if result.returncode != 0:
        return "down"
    status = result.stdout.strip()
    if status != "running":
        return status

    health = subprocess.run(
        ["docker", "inspect", name, "--format", "{{.State.Health.Status}}"],
        capture_output=True, text=True, timeout=5,
    )
    h = health.stdout.strip()
    if not h or h == "<nil>":
        return "healthy"
    if h == "healthy":
        return "healthy"
    return f"degraded({h})"


def check_systemd(name: str) -> str:
    result = subprocess.run(
        ["systemctl", "is-active", name],
        capture_output=True, text=True, timeout=10,
    )
    status = result.stdout.strip()
    return "healthy" if status == "active" else f"down({status})"


def check_disk() -> dict:
    result = subprocess.run(
        ["df", "/"], capture_output=True, text=True, timeout=5,
    )
    lines = result.stdout.strip().split("\n")
    if len(lines) >= 2:
        parts = lines[1].split()
        usage = int(parts[4].rstrip("%")) if len(parts) >= 5 else 0
        return {"usage_pct": usage, "status": "ok" if usage <= 85 else "warning"}
    return {"usage_pct": 0, "status": "unknown"}


def load_previous() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except (json.JSONDecodeError, ValueError):
            pass
    return {}


def check_all() -> dict:
    state = {}
    for name, kind in SERVICES:
        if kind == "docker":
            state[name] = check_docker(name)
        elif kind == "systemd":
            state[name] = check_systemd(name)
    disk = check_disk()
    state["disk"] = f"{disk['usage_pct']}%"
    state["disk_status"] = disk["status"]
    return state


def run(interval: int = 300):
    prev = load_previous()
    print(f"[ops] Monitor started — interval={interval}s")

    while True:
        current = check_all()

        for key, val in current.items():
            pval = prev.get(key, "")
            if val == pval:
                continue

            if key == "disk_status":
                if val == "warning" and pval == "ok":
                    emit("system:disk:warning", {"usage": current.get("disk", "?")})
            elif key == "disk":
                continue
            elif "down" in val and ("down" not in pval):
                emit("system:service:down", {"service": key, "status": val})
            elif val == "healthy" and "down" in pval:
                emit("system:service:recovered", {"service": key, "from": pval, "to": val})

        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(current, indent=2))

        try:
            from ops.supabase_emitter import emit_service_status
            emit_service_status(current)
        except Exception:
            pass

        prev = current

        if "--once" in sys.argv:
            break
        time.sleep(interval)


if __name__ == "__main__":
    interval = 300
    for i, arg in enumerate(sys.argv):
        if arg == "--interval" and i + 1 < len(sys.argv):
            interval = int(sys.argv[i + 1])
    run(interval)
