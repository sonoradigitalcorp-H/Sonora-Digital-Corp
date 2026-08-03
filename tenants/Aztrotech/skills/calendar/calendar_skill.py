"""Calendar Skill — Google Calendar integration for César's availability."""
import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional

logger = logging.getLogger("calendar-skill")

CREDS_PATH = os.getenv("GOOGLE_CALENDAR_CREDS", "")
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", "primary")


def get_calendar_service():
    """Create Google Calendar service."""
    if not CREDS_PATH or not os.path.exists(CREDS_PATH):
        logger.warning("Google Calendar creds not found")
        return None
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        scopes = ["https://www.googleapis.com/auth/calendar.readonly",
                   "https://www.googleapis.com/auth/calendar.events"]
        creds = service_account.Credentials.from_service_account_file(
            CREDS_PATH, scopes=scopes
        )
        return build("calendar", "v3", credentials=creds)
    except Exception as e:
        logger.error(f"Calendar service error: {e}")
        return None


def get_available_slots(date_str: str = None) -> List[Dict]:
    """Get available 30-min slots for a given day (8am-6pm)."""
    service = get_calendar_service()
    if not service:
        # Fallback: return all slots 8am-6pm
        return _default_slots(date_str)
    
    try:
        if date_str:
            target = datetime.strptime(date_str, "%Y-%m-%d")
        else:
            target = datetime.now() + timedelta(days=1)
        
        start = target.replace(hour=8, minute=0, second=0, microsecond=0)
        end = target.replace(hour=18, minute=0, second=0, microsecond=0)
        
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=start.isoformat() + "Z",
            timeMax=end.isoformat() + "Z",
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        
        busy_slots = []
        for event in events_result.get("items", []):
            ev_start = event["start"].get("dateTime", event["start"].get("date"))
            ev_end = event["end"].get("dateTime", event["end"].get("date"))
            busy_slots.append({
                "start": datetime.fromisoformat(ev_start.replace("Z", "+00:00")),
                "end": datetime.fromisoformat(ev_end.replace("Z", "+00:00"))
            })
        
        # Generate available slots
        available = []
        current = start
        while current < end:
            slot_end = current + timedelta(minutes=30)
            is_free = True
            for busy in busy_slots:
                if current < busy["end"] and slot_end > busy["start"]:
                    is_free = False
                    break
            if is_free:
                available.append({
                    "time": current.strftime("%I:%M %p"),
                    "hour": current.hour,
                    "minute": current.minute,
                    "period": "morning" if current.hour < 12 else "afternoon",
                    "date": target.strftime("%Y-%m-%d")
                })
            current = slot_end
        
        return available
    except Exception as e:
        logger.error(f"Error getting slots: {e}")
        return _default_slots(date_str)


def _default_slots(date_str=None) -> List[Dict]:
    """Default slots when calendar is not connected."""
    if date_str:
        target = datetime.strptime(date_str, "%Y-%m-%d")
    else:
        target = datetime.now() + timedelta(days=1)
    
    slots = []
    for h in range(8, 18):
        for m in [0, 30]:
            t = target.replace(hour=h, minute=m)
            slots.append({
                "time": t.strftime("%I:%M %p"),
                "hour": h, "minute": m,
                "period": "morning" if h < 12 else "afternoon",
                "date": target.strftime("%Y-%m-%d")
            })
    return slots


def create_event(date_str: str, time_str: str, client_name: str, client_phone: str = "") -> Dict:
    """Create a calendar event for the call."""
    service = get_calendar_service()
    if not service:
        return {"ok": False, "error": "Calendar not connected"}
    
    try:
        # Parse time
        target = datetime.strptime(date_str, "%Y-%m-%d")
        time_parts = time_str.replace("AM","").replace("PM","").strip().split(":")
        hour = int(time_parts[0])
        minute = int(time_parts[1]) if len(time_parts) > 1 else 0
        if "PM" in time_str and hour < 12:
            hour += 12
        
        start = target.replace(hour=hour, minute=minute)
        end = start + timedelta(minutes=15)
        
        event = {
            "summary": f"Llamada con {client_name}",
            "description": f"Llamada de prospecto.\nNombre: {client_name}\nTeléfono: {client_phone}\nAgendado vía Asistente Aztrotech",
            "start": {"dateTime": start.isoformat(), "timeZone": "America/Hermosillo"},
            "end": {"dateTime": end.isoformat(), "timeZone": "America/Hermosillo"},
        }
        
        result = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        return {"ok": True, "event_id": result.get("id"), "link": result.get("htmlLink")}
    except Exception as e:
        logger.error(f"Create event error: {e}")
        return {"ok": False, "error": str(e)}


if __name__ == "__main__":
    slots = get_available_slots()
    print(f"Available slots: {len(slots)}")
    for s in slots[:5]:
        print(f"  {s['time']} ({s['period']})")
