"""Event Handler: alerts on error/critical events (HAS-003)"""
import json
from pathlib import Path
from typing import Any

from events.handlers.base import EventHandler

REPO = Path(__file__).resolve().parent.parent.parent


class AlertHandler(EventHandler):
    name = "alert"

    def __init__(self):
        self._alerts: list[dict] = []
        self._alert_dir = REPO / "state" / "alerts"
        self._alert_dir.mkdir(parents=True, exist_ok=True)

    async def handle(self, event: dict) -> None:
        evt_type = event.get("type", event.get("event", ""))
        severity = "info"
        if "error" in evt_type or "failed" in evt_type or "violation" in evt_type:
            severity = "critical"
        elif "warn" in evt_type:
            severity = "warning"

        if severity in ("critical", "warning"):
            alert = {
                "id": event.get("id"),
                "type": evt_type,
                "severity": severity,
                "message": str(event.get("payload", event.get("subject", {})))[:200],
                "timestamp": event.get("timestamp", ""),
            }
            self._alerts.append(alert)
            path = self._alert_dir / f"{event.get('id', 'alert')}.json"
            path.write_text(json.dumps(alert, indent=2))

            if len(self._alerts) > 100:
                self._alerts.pop(0)

    def recent_alerts(self, limit: int = 10) -> list[dict]:
        return self._alerts[-limit:]
