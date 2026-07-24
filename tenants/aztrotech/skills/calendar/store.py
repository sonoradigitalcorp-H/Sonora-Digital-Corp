import json
import os
from datetime import datetime
from typing import Optional
from .models import Booking, BookingSlot
from .notify import notify_cesar

BOOKINGS_FILE = os.path.join(os.path.dirname(__file__), "bookings.json")


def _load_bookings() -> list[dict]:
    if not os.path.exists(BOOKINGS_FILE):
        return []
    with open(BOOKINGS_FILE) as f:
        return json.load(f)


def _save_bookings(bookings: list[dict]):
    os.makedirs(os.path.dirname(BOOKINGS_FILE), exist_ok=True)
    with open(BOOKINGS_FILE, "w") as f:
        json.dump(bookings, f, indent=2, default=str)


def create_booking(booking: Booking, silent: bool = False) -> Booking:
    bookings = _load_bookings()
    booking.id = f"bk_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{len(bookings) + 1}"
    booking.created_at = datetime.utcnow()
    bookings.append(booking.model_dump(mode="json"))
    _save_bookings(bookings)
    if not silent:
        notify_cesar(booking)
    return booking


def get_bookings_for_date(target_date) -> list[Booking]:
    date_str = str(target_date)
    bookings = _load_bookings()
    result = []
    for b in bookings:
        slot_date = b.get("slot", {}).get("date", "")
        if slot_date == date_str and b.get("status") == "confirmed":
            result.append(Booking(**b))
    return result


def get_all_bookings() -> list[Booking]:
    return [Booking(**b) for b in _load_bookings()]


def cancel_booking(booking_id: str) -> Optional[Booking]:
    bookings = _load_bookings()
    for b in bookings:
        if b.get("id") == booking_id:
            b["status"] = "cancelled"
            _save_bookings(bookings)
            return Booking(**b)
    return None
