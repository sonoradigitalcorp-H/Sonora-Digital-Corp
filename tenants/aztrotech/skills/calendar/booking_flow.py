"""Mystic booking flow — handles the voice/text conversation for scheduling."""

from datetime import date, timedelta, datetime
from typing import Optional
from .models import Booking, BookingSlot, AvailabilityConfig
from .availability import get_available_slots, get_available_days
from .store import create_booking

config = AvailabilityConfig()


def start() -> str:
    today = date.today()
    days = get_available_days(days_ahead=14)
    if not days:
        return "Lo siento, no hay días disponibles en las próximas dos semanas."

    day_names = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    lines = []
    for d in days[:7]:
        slots = get_available_slots(d)
        if slots:
            name = day_names[d.weekday()]
            times = ", ".join(f"{s.start_time.strftime('%H:%M')}" for s in slots[:4])
            lines.append(f"{name} {d.day}/{d.month}: {times}")

    return "Estos son los horarios disponibles de César:\n" + "\n".join(lines)


def show_slots_for_day(target_date: date) -> Optional[list[BookingSlot]]:
    return get_available_slots(target_date)


def confirm_booking(
    prospect_name: str,
    prospect_email: str,
    slot: BookingSlot,
    prospect_phone: Optional[str] = None,
    company: Optional[str] = None,
    notes: Optional[str] = None,
) -> Booking:
    booking = Booking(
        id="",
        created_at=datetime.utcnow(),
        prospect_name=prospect_name,
        prospect_email=prospect_email,
        prospect_phone=prospect_phone,
        company=company,
        slot=slot,
        notes=notes,
    )
    return create_booking(booking)


def format_slot(slot: BookingSlot) -> str:
    day_names = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    weekday = slot.date.weekday()
    return f"{day_names[weekday]} {slot.date.day}/{slot.date.month} a las {slot.start_time.strftime('%H:%M')}"
