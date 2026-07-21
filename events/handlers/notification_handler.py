import json
import logging
from pathlib import Path
from typing import Any

log = logging.getLogger("events.notification_handler")

NOTIFIER_FILE = Path("state/notifier/queue.jsonl")
NOTIFIER_FILE.parent.mkdir(parents=True, exist_ok=True)

NOTIFIABLE_TYPES = {
    "system:alert", "agent:task:failed", "container:down",
    "service:degraded", "security:violation", "evolution:proposal",
}


class NotificationHandler:
    def handle(self, event: dict[str, Any]) -> None:
        etype = event.get("type", "")
        if etype not in NOTIFIABLE_TYPES:
            return
        notification = {
            "type": etype,
            "channel": "telegram" if "security" in etype or "alert" in etype else "whatsapp",
            "priority": "high" if "alert" in etype or "violation" in etype else "normal",
            "target": "founder",
            "message": event.get("payload", {}).get("message", str(event)),
            "timestamp": event.get("timestamp", ""),
        }
        try:
            with open(NOTIFIER_FILE, "a") as f:
                f.write(json.dumps(notification) + "\n")
            log.info("Notification queued: %s -> %s", etype, notification["channel"])
        except Exception as e:
            log.error("Failed to queue notification: %s", e)
