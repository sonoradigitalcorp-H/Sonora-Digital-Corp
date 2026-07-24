from datetime import date, datetime, time, timedelta
from typing import Optional
from .models import AvailabilityConfig, BookingSlot
from .store import get_bookings_for_date


def get_available_slots(
    target_date: date,
    config: Optional[AvailabilityConfig] = None,
) -> list[BookingSlot]:
    if config is None:
        config = AvailabilityConfig()

    weekday = target_date.weekday()

    if weekday < 5:
        range_str = config.monday_friday
    elif weekday == 5:
        range_str = config.saturday
    else:
        if config.sunday:
            range_str = config.sunday
        else:
            return []

    start_str, end_str = range_str
    start_h, start_m = map(int, start_str.split(":"))
    end_h, end_m = map(int, end_str.split(":"))

    start_time = time(start_h, start_m)
    end_time = time(end_h, end_m)

    existing = get_bookings_for_date(target_date)
    booked_slots = []
    for b in existing:
        s = b.slot
        booked_slots.append((
            _time_to_minutes(s.start_time),
            _time_to_minutes(s.end_time),
        ))

    slots = []
    current = _time_to_minutes(start_time)
    end = _time_to_minutes(end_time)
    duration = config.slot_duration_minutes

    while current + duration <= end:
        slot_start = _minutes_to_time(current)
        slot_end = _minutes_to_time(current + duration)

        if not _is_overlapping(current, current + duration, booked_slots):
            now = datetime.utcnow()
            if target_date > now.date() or (target_date == now.date() and current >= _time_to_minutes(now.time())):
                slots.append(BookingSlot(
                    date=target_date,
                    start_time=slot_start,
                    end_time=slot_end,
                ))

        current += duration

    return slots


def get_available_days(
    days_ahead: int = 14,
    config: Optional[AvailabilityConfig] = None,
) -> list[date]:
    if config is None:
        config = AvailabilityConfig()

    today = date.today()
    available = []
    for i in range(days_ahead + 1):
        d = today + timedelta(days=i)
        weekday = d.weekday()
        if weekday < 5:
            available.append(d)
        elif weekday == 5:
            available.append(d)
        else:
            if config.sunday:
                available.append(d)
    return available


def _time_to_minutes(t: time) -> int:
    return t.hour * 60 + t.minute


def _minutes_to_time(m: int) -> time:
    return time(m // 60, m % 60)


def _is_overlapping(start: int, end: int, booked: list[tuple[int, int]]) -> bool:
    for bs, be in booked:
        if start < be and end > bs:
            return True
    return False
