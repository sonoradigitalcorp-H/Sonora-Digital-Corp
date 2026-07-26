from datetime import date, time, datetime, timedelta
from typing import Optional
from pydantic import BaseModel


class BookingSlot(BaseModel):
    date: date
    start_time: time
    end_time: time


class BookingRequest(BaseModel):
    prospect_name: str
    prospect_email: str
    prospect_phone: Optional[str] = None
    company: Optional[str] = None
    slot: BookingSlot
    notes: Optional[str] = None


class Booking(BaseModel):
    id: str
    created_at: datetime
    prospect_name: str
    prospect_email: str
    prospect_phone: Optional[str] = None
    company: Optional[str] = None
    slot: BookingSlot
    notes: Optional[str] = None
    status: str = "confirmed"  # confirmed, cancelled, completed


class AvailabilityConfig(BaseModel):
    monday_friday: tuple[str, str] = ("09:00", "18:00")
    saturday: tuple[str, str] = ("09:00", "14:00")
    sunday: Optional[tuple[str, str]] = None
    slot_duration_minutes: int = 15
    buffer_minutes: int = 0
    max_days_ahead: int = 30
