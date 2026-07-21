from fastapi import APIRouter, Request
from pydantic import BaseModel
from database import query_db
import json

router = APIRouter(prefix="/api", tags=["tracking"])

class TrackEvent(BaseModel):
    section: str
    action: str
    metadata: dict = {}

@router.post("/track")
async def track_event(event: TrackEvent, request: Request):
    ip = request.client.host if request.client else "unknown"
    query_db(
        "INSERT INTO section_interactions (section, action, metadata, session_id, ip) "
        "VALUES (:section, :action, CAST(:metadata AS jsonb), :session_id, :ip)",
        params={
            "section": event.section,
            "action": event.action,
            "metadata": json.dumps(event.metadata),
            "session_id": request.headers.get("x-session-id", ""),
            "ip": ip,
        },
    )
    return {"status": "ok"}

@router.get("/track/stats")
async def track_stats():
    rows = query_db(
        "SELECT section, action, COUNT(*) as count, "
        "DATE(created_at) as date "
        "FROM section_interactions "
        "GROUP BY section, action, DATE(created_at) "
        "ORDER BY date DESC, count DESC "
        "LIMIT 50"
    )
    return rows
