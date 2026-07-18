#!/usr/bin/env python3
"""Healer — Auto-repair de containers caídos.

Lee container_down events, intenta docker restart, verifica health.
Si falla 3 veces, escribe container_critical (n8n lo toma para Telegram).
"""
import json
import logging
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("healer")

BASE = Path(__file__).resolve().parent.parent
EVENTS_FILE = BASE / "state" / "logs" / "events.jsonl"
MEMORY_EVENTS = BASE / "memory" / "learning" / "events.jsonl"

RESTART_TIMEOUT = 30  # seconds to wait after restart
POLL_INTERVAL = 10    # seconds between health polls
MAX_RETRIES = 3       # restart attempts before critical
DEDUP_WINDOW = 300    # seconds — ignore events older than this
HEALER_COOLDOWN = 120 # seconds — skip container if healed recently


def read_events(max_lines: int = 100) -> list[dict]:
    """Read recent events from events.jsonl."""
    if not EVENTS_FILE.exists():
        return []
    with open(EVENTS_FILE) as f:
        lines = f.readlines()[-max_lines:]
    events = []
    for line in lines:
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def emit_event(event: dict):
    event["timestamp"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EVENTS_FILE, "a") as f:
        f.write(json.dumps(event) + "\n")
    MEMORY_EVENTS.parent.mkdir(parents=True, exist_ok=True)
    with open(MEMORY_EVENTS, "a") as f:
        f.write(json.dumps({"event": event.get("type"), "timestamp": event["timestamp"], "payload": event}) + "\n")


def docker_ps(container: str) -> tuple[bool, str]:
    """Check if container is running and healthy. Returns (healthy, status_str)."""
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", f"name={container}", "--format", "{{.Status}}"],
            capture_output=True, text=True, timeout=10,
        )
        status = result.stdout.strip()
        if not status:
            return False, "not_found"
        return "healthy" in status or "Up" in status, status
    except subprocess.TimeoutExpired:
        return False, "timeout"
    except FileNotFoundError:
        return False, "docker_not_found"


def docker_restart(container: str) -> bool:
    """Restart container, return True if command succeeded."""
    try:
        result = subprocess.run(
            ["docker", "restart", container],
            capture_output=True, text=True, timeout=RESTART_TIMEOUT,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def check_recent_healing(container: str) -> bool:
    """Check if we already healed this container recently (dedup)."""
    events = read_events(200)
    now = time.time()
    for e in reversed(events):
        if e.get("type") == "healing_success" and e.get("container") == container:
            ts = datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00")).timestamp()
            if now - ts < HEALER_COOLDOWN:
                return True
    return False


def send_telegram(container: str, attempt: int):
    """Send critical alert to Luis Daniel via Telegram."""
    token = os.getenv("ABE_FENIX_BOT_TOKEN", "").strip()
    chat_id = os.getenv("ABE_TELEGRAM_CHAT", "").strip()

    if not token or not chat_id:
        # Fallback: try loading from .env
        env_path = Path(__file__).resolve().parent.parent / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("ABE_FENIX_BOT_TOKEN="):
                    token = line.split("=", 1)[1].strip().strip('"')
                elif line.startswith("ABE_TELEGRAM_CHAT="):
                    chat_id = line.split("=", 1)[1].strip().strip('"')

    if not token or not chat_id:
        log.warning("Telegram not configured — no token or chat_id")
        return

    message = (
        f"🔴 <b>CONTAINER CRITICAL</b>\n"
        f"<code>{container}</code>\n"
        f"Intentos de reparacion: {attempt}\n"
        f"No revive automaticamente.\n"
        f"Servidor: sdc-prod (149.56.46.173)"
    )

    try:
        import httpx
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        resp = httpx.post(url, json={
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
        }, timeout=15)
        if resp.status_code == 200:
            log.info(f"Telegram sent for {container}")
        else:
            log.warning(f"Telegram returned {resp.status_code}: {resp.text[:100]}")
    except Exception as e:
        log.warning(f"Telegram failed: {e}")


def main():
    recent = read_events(100)
    now_ts = datetime.now(timezone.utc).timestamp()

    # Find recent container_down events
    down_containers = set()
    for e in recent:
        if e.get("type") == "container_down":
            ts = datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00")).timestamp()
            if now_ts - ts < DEDUP_WINDOW:
                down_containers.add(e.get("container", ""))

    if not down_containers:
        log.info("No containers to heal")
        return

    for container in sorted(down_containers):
        log.info(f"Processing: {container}")

        # Skip if already running
        is_healthy, status = docker_ps(container)
        if is_healthy:
            log.info(f"  {container} already healthy ({status}) — skipping")
            continue

        # Skip if recently healed
        if check_recent_healing(container):
            log.info(f"  {container} recently healed — skipping (cooldown)")
            continue

        for attempt in range(1, MAX_RETRIES + 1):
            emit_event({
                "type": "healing_attempt",
                "container": container,
                "attempt": attempt,
            })
            log.info(f"  Attempt {attempt}/{MAX_RETRIES}: docker restart {container}")

            ok = docker_restart(container)
            if not ok:
                log.warning("  docker restart command failed")
                continue

            # Poll for health
            for _ in range(RESTART_TIMEOUT // POLL_INTERVAL):
                time.sleep(POLL_INTERVAL)
                is_healthy, status = docker_ps(container)
                if is_healthy:
                    emit_event({
                        "type": "healing_success",
                        "container": container,
                        "attempt": attempt,
                        "status": status,
                    })
                    log.info(f"  ✅ {container} revived (attempt {attempt})")
                    break
            else:
                # Loop didn't break — still not healthy
                log.warning(f"  Attempt {attempt} failed for {container}")
                continue
            break  # Success — exit retry loop
        else:
            # All attempts failed
            emit_event({
                "type": "healing_failure",
                "container": container,
                "attempts": MAX_RETRIES,
            })
            emit_event({
                "type": "container_critical",
                "container": container,
                "attempts": MAX_RETRIES,
                "message": f"Container {container} down after {MAX_RETRIES} restart attempts",
            })
            log.error(f"  🔴 {container}: CRITICAL — sending Telegram")
            send_telegram(container, MAX_RETRIES)


if __name__ == "__main__":
    main()
