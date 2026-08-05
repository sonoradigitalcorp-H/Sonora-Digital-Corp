"""Event routes."""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class EventRequest(BaseModel):
    """Event request model."""
    type: str
    source: str
    payload: dict
    metadata: dict = {}


class EventResponse(BaseModel):
    """Event response model."""
    id: str
    type: str
    source: str
    payload: dict
    metadata: dict
    timestamp: str


# In-memory store for demo (will be replaced with Redis Streams)
events_store: list[EventResponse] = []


@router.post("/events", response_model=EventResponse)
async def publish_event(request: EventRequest):
    """Publish an event."""
    event = EventResponse(
        id=str(uuid4()),
        type=request.type,
        source=request.source,
        payload=request.payload,
        metadata=request.metadata,
        timestamp=datetime.utcnow().isoformat()
    )

    events_store.append(event)
    return event


@router.get("/events", response_model=list[EventResponse])
async def list_events(
    type: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = 10
):
    """List events with optional filters."""
    events = events_store.copy()

    if type:
        events = [e for e in events if e.type == type]
    if source:
        events = [e for e in events if e.source == source]

    return events[-limit:]  # Return most recent


@router.get("/events/stats")
async def event_stats():
    """Get event statistics."""
    stats = {}
    for event in events_store:
        stats[event.type] = stats.get(event.type, 0) + 1

    return {
        "total_events": len(events_store),
        "events_by_type": stats
    }
