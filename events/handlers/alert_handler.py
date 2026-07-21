import json
import logging
from pathlib import Path
from typing import Any

log = logging.getLogger("events.alert_handler")

ALERTS_DIR = Path("state/alerts")
ALERTS_DIR.mkdir(parents=True, exist_ok=True)

CRITICAL_TYPES = {"error", "failed", "violation", "critical"}
WARN_TYPES = {"warn", "warning", "degraded"}


class AlertHandler:
    def handle(self, event: dict[str, Any]) -> None:
        etype = event.get("type", "")
        severity = "critical" if any(t in etype for t in CRITICAL_TYPES) else \
                   "warning" if any(t in etype for t in WARN_TYPES) else "info"
        if severity == "info":
            return
        alert = {
            "severity": severity,
            "type": etype,
            "source": event.get("source", ""),
            "ts": event.get("timestamp", ""),
            "payload": event.get("payload", {}),
            "message": event.get("payload", {}).get("message", str(event)),
        }
        path = ALERTS_DIR / f"alert-{event.get('timestamp', 'unknown')}.json"
        try:
            with open(path, "w") as f:
                json.dump(alert, f, indent=2)
            log.info("Alert saved: %s (%s)", etype, severity)
        except Exception as e:
            log.error("Failed to save alert: %s", e)
