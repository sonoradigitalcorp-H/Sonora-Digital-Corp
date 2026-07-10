from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from capabilities.bus.router import load_registry, route, get_capability

router = APIRouter(prefix="/api/v1/capability-bus", tags=["capability-bus"])


class RouteRequest(BaseModel):
    query: str
    context: dict = {}


@router.get("/capabilities")
async def list_capabilities():
    registry = load_registry()
    return {"capabilities": registry.get("capabilities", [])}


@router.get("/capabilities/{cap_id}")
async def get_capability_endpoint(cap_id: str):
    cap = get_capability(cap_id)
    if not cap:
        raise HTTPException(status_code=404, detail=f"Capability '{cap_id}' not found")
    return cap


@router.post("/route")
async def route_endpoint(req: RouteRequest):
    result = route(req.query, req.context)
    if result["status"] == "no_match":
        raise HTTPException(status_code=404, detail=result)
    if result["status"] == "policy_blocked":
        raise HTTPException(status_code=403, detail=result)
    return result
