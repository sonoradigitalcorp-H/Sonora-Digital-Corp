"""Notifier Worker — HAS-003
Listens to the event bus and dispatches proactive notifications via OpenClaw bridge.
"""
import json
import os
import time
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EVENTS_FILE = REPO / "state" / "events" / "events.jsonl"
OPENCLAW_URL = os.getenv("OPENCLAW_URL", "http://localhost:18789")
OPENCLAW_API_KEY = os.getenv("OPENCLAW_API_KEY", "")
POLL_INTERVAL = int(os.getenv("NOTIFIER_POLL_INTERVAL", "10"))


def get_last_event_id():
    state_file = REPO / "state" / "notifier_last_event.txt"
    if state_file.exists():
        return int(state_file.read_text().strip())
    return 0


def save_last_event_id(event_id: int):
    state_file = REPO / "state" / "notifier_last_event.txt"
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(str(event_id))


def call_openclaw(skill: str, params: dict) -> bool:
    """Bridge: calls an OpenClaw skill via its REST API."""
    try:
        data = json.dumps({"command": f"/{skill}", "args": params}).encode()
        req = urllib.request.Request(
            f"{OPENCLAW_URL}/api/execute",
            data=data,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {OPENCLAW_API_KEY}"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[notifier] OpenClaw call failed: {e}")
        return False


def should_notify(event: dict) -> bool:
    event_type = event.get("event", "")
    critical = event.get("critical", False)

    notify_events = {
        "clone.training.completed",
        "video.generation.completed",
        "sync.failed",
        "payment.failed",
    }

    return event_type in notify_events or critical


def process_event(event: dict):
    event_id = event.get("id", 0)
    event_type = event.get("event", "")

    if not should_notify(event):
        return

    skill_map = {
        "clone.training.completed": "speckit.specify",
        "video.generation.completed": "speckit.specify",
        "sync.failed": "speckit.tasks",
        "payment.failed": "speckit.tasks",
    }

    skill = skill_map.get(event_type, "speckit.tasks")
    params = {"event": event_type, "data": event.get("data", {})}

    print(f"[notifier] Dispatching {event_type} -> {skill}")
    success = call_openclaw(skill, params)
    if success:
        print(f"[notifier] ✅ {event_id} dispatched")
    else:
        print(f"[notifier] ❌ {event_id} failed")


def poll():
    print(f"[notifier] Starting. Polling {EVENTS_FILE} every {POLL_INTERVAL}s")
    last_id = get_last_event_id()

    while True:
        if EVENTS_FILE.exists():
            with open(EVENTS_FILE) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        event = json.loads(line)
                        event_id = event.get("id", 0)
                        if event_id > last_id:
                            process_event(event)
                            last_id = event_id
                            save_last_event_id(last_id)
                    except json.JSONDecodeError:
                        continue

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    poll()
