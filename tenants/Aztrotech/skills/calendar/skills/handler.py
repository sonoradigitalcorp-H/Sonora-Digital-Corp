"""calendar handler — Calendar & Booking
Agendamiento de citas y reuniones.
"""
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent.parent.parent
STORE_PATH = REPO / "state" / "calendar" / "bookings.json"

SLOTS = ["09:00", "10:00", "11:00", "12:00", "14:00", "15:00", "16:00", "17:00"]


def _ensure():
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not STORE_PATH.exists():
        STORE_PATH.write_text("[]")


def _load() -> list[dict]:
    _ensure()
    return json.loads(STORE_PATH.read_text())


def _save(data: list[dict]):
    _ensure()
    STORE_PATH.write_text(json.dumps(data, indent=2, default=str))


async def execute(context: Any) -> dict:
    input_data = context if isinstance(context, dict) else {}
    action = input_data.get("action", "list")

    if action == "available":
        date = input_data.get("date", "")
        bookings = _load()
        booked = {b["time"] for b in bookings if b["date"] == date}
        return {"action": "available", "date": date, "slots": [s for s in SLOTS if s not in booked]}

    elif action == "book":
        booking = {
            "id": str(uuid.uuid4()),
            "date": input_data.get("date", ""),
            "time": input_data.get("time", ""),
            "client_name": input_data.get("client_name", ""),
            "client_contact": input_data.get("client_contact", ""),
            "notes": input_data.get("notes", ""),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        bookings = _load()
        bookings.append(booking)
        _save(bookings)
        return {"action": "book", "booking": booking, "total": len(bookings)}

    elif action == "list":
        bookings = _load()
        date_filter = input_data.get("date", "")
        if date_filter:
            bookings = [b for b in bookings if b["date"] == date_filter]
        return {"action": "list", "bookings": bookings, "total": len(bookings)}

    return {"action": action, "error": f"Unknown action: {action}"}
