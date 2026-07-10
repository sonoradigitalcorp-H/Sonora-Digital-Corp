from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from apps.understand.knowledge import search_all_sources, recent_sessions, synthesize
from apps.understand.pipeline import consume_observe_events
from apps.understand.truth import load_constitution, verify_against_constitution

router = APIRouter(prefix="/api/v1/understand", tags=["understand"])


class QueryRequest(BaseModel):
    query: str
    context: dict = {}


@router.get("/status")
async def status():
    constitution = load_constitution()
    events = consume_observe_events()
    sessions = recent_sessions(3)
    return {
        "service": "understand-kernel",
        "level": 2,
        "constitution_files": len(constitution),
        "pending_events": len(events),
        "recent_sessions": sessions,
        "status": "operational",
    }


@router.post("/search")
async def search(req: QueryRequest):
    results = search_all_sources(req.query)
    return {"query": req.query, "results": results, "count": len(results)}


@router.post("/synthesize")
async def synthesize_endpoint(req: QueryRequest):
    return synthesize(req.context, req.query)


@router.post("/verify")
async def verify(data: dict):
    return verify_against_constitution(data)
