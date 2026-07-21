import logging

from fastapi import APIRouter, Depends, HTTPException

from ..config import config
from ..core.abe_service import abe_service
from ..models import (
    CEODashboard,
    ChatRequest,
    ContractType,
    Role,
    TokenPayload,
)
from .middleware import create_token, require_role

log = logging.getLogger("abe.api")
router = APIRouter(prefix="/api")


@router.get("/health")
async def health():
    from ..bridges.mcp import health as mcp_health
    mcp = await mcp_health()
    return {
        "status": "ok",
        "service": "ABE Music OS",
        "powered_by": "Sonora Digital Corp",
        "mcp_gateway": mcp.get("status", "unavailable"),
    }


_DEMO_USERS = {
    "abraham": {"role": "ceo"},
    "director": {"role": "director"},
    "artista": {"role": "artista"},
}

@router.post("/auth/login")
async def auth_login(data: dict):
    user_id = data.get("user_id", "").strip().lower()

    if user_id not in _DEMO_USERS:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    role_str = _DEMO_USERS[user_id]["role"]
    token = create_token({"sub": user_id, "role": role_str, "tenant": "abe-fenix"})
    return {"access_token": token, "token_type": "Bearer", "role": role_str}


@router.post("/auth/token")
async def auth_token(data: dict):
    user_id = data.get("user_id", "")
    role_str = data.get("role", "fan")
    secret = data.get("secret", "")

    if secret != config.jwt_secret:
        raise HTTPException(status_code=401, detail="Invalid secret")

    try:
        role = Role(role_str)
    except ValueError:
        role = Role.FAN

    token = create_token({"sub": user_id, "role": role.value, "tenant": "abe-fenix"})
    return {"access_token": token, "token_type": "Bearer", "role": role.value}


@router.get("/ceo/dashboard", response_model=CEODashboard)
async def ceo_dashboard(payload: TokenPayload = Depends(require_role(Role.CEO))):
    return abe_service.get_ceo_dashboard()


@router.get("/artists")
async def list_artists(
    status: str = None,
    payload: TokenPayload = Depends(require_role(Role.DIRECTOR)),
):
    return {"artists": abe_service.get_artists(status)}


@router.get("/artists/{artist_id}")
async def get_artist(
    artist_id: str,
    payload: TokenPayload = Depends(require_role(Role.ARTISTA)),
):
    artist = abe_service.get_artist(artist_id)
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    return artist


@router.get("/artists/{artist_id}/kpi")
async def artist_kpi(
    artist_id: str,
    payload: TokenPayload = Depends(require_role(Role.ARTISTA)),
):
    artist = abe_service.get_artist(artist_id)
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    releases = abe_service.get_releases(artist_id)
    return {
        "artist": artist.get("nombre"),
        "status": artist.get("status"),
        "total_streams": artist.get("streams", 0),
        "total_revenue": artist.get("revenue", 0),
        "releases": len(releases),
        "genre": artist.get("genero"),
        "monthly_listeners": artist.get("monthly_listeners", 0),
    }


@router.get("/artists/{artist_id}/releases")
async def artist_releases(
    artist_id: str,
    payload: TokenPayload = Depends(require_role(Role.ARTISTA)),
):
    return {"releases": abe_service.get_releases(artist_id)}


@router.post("/artists/{artist_id}/streams")
async def record_stream(
    artist_id: str,
    data: dict,
    payload: TokenPayload = Depends(require_role(Role.DIRECTOR)),
):
    release_id = data.get("release_id", "")
    amount = data.get("amount", 1)
    return abe_service.record_stream(release_id, amount)


@router.post("/chat")
async def chat(
    req: ChatRequest,
    payload: TokenPayload = Depends(require_role(Role.FAN)),
):
    result = await abe_service.chat.process(
        req.text,
        session_id=req.session_id,
        context={**req.context, "role": payload.role.value, "user_id": payload.sub},
    )
    return result


@router.post("/voice/process")
async def voice_process(data: dict):
    session_id = data.get("session_id")
    audio_b64 = data.get("audio", "")
    final = data.get("final", False)
    return await abe_service.voice.process_chunk(audio_b64, session_id, final=final)


@router.get("/contracts")
async def list_contracts(
    artist_id: str = None,
    status: str = None,
    payload: TokenPayload = Depends(require_role(Role.DIRECTOR)),
):
    return {"contracts": abe_service.contracts.list_contracts(artist_id, status)}


@router.post("/contracts")
async def create_contract(
    data: dict,
    payload: TokenPayload = Depends(require_role(Role.DIRECTOR)),
):
    contract = abe_service.contracts.create_contract(
        artist_id=data["artist_id"],
        contract_type=ContractType(data.get("type", "distribution_only")),
        revenue_splits=data.get("revenue_splits"),
        start_date=data.get("start_date"),
        end_date=data.get("end_date"),
        territories=data.get("territories"),
        platforms=data.get("platforms"),
    )
    return contract


@router.get("/contracts/{contract_id}")
async def get_contract(contract_id: str):
    contract = abe_service.contracts.get_contract(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract


@router.post("/contracts/{contract_id}/sign")
async def sign_contract(
    contract_id: str,
    payload: TokenPayload = Depends(require_role(Role.DIRECTOR)),
):
    contract = abe_service.contracts.update_status(contract_id, "active")
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract


@router.get("/revenue")
async def revenue_summary(
    artist_id: str = None,
    payload: TokenPayload = Depends(require_role(Role.DIRECTOR)),
):
    return abe_service.revenue.summary(artist_id)


@router.post("/revenue/record")
async def record_revenue(
    data: dict,
    payload: TokenPayload = Depends(require_role(Role.DIRECTOR)),
):
    return abe_service.revenue.record(
        contract_id=data["contract_id"],
        artist_id=data["artist_id"],
        release_id=data.get("release_id", ""),
        amount=data["amount"],
        source=data.get("source", "streaming"),
    )


@router.get("/distribution/releases")
async def distribution_releases(
    artist_id: str = None,
    status: str = None,
    payload: TokenPayload = Depends(require_role(Role.DIRECTOR)),
):
    return {"releases": abe_service.distribution.list_releases(artist_id, status)}


@router.post("/distribution/releases")
async def create_distribution_release(
    data: dict,
    payload: TokenPayload = Depends(require_role(Role.DIRECTOR)),
):
    return abe_service.distribution.create_release(
        artist_id=data["artist_id"],
        title=data["title"],
        album_type=data.get("type", "single"),
        genre=data.get("genre", ""),
        upc=data.get("upc"),
        isrc=data.get("isrc"),
        platforms=data.get("platforms"),
    )


@router.get("/crm/fans")
async def list_fans(
    query: str = "",
    payload: TokenPayload = Depends(require_role(Role.DIRECTOR)),
):
    return {"fans": abe_service.crm.search_fans(query)}


@router.get("/crm/fans/summary")
async def fan_summary(
    payload: TokenPayload = Depends(require_role(Role.CEO)),
):
    return abe_service.crm.fan_summary()


@router.get("/openclaw/health")
async def openclaw_health():
    from ..bridges.openclaw import health as oc_health
    return await oc_health()


@router.get("/openclaw/skills")
async def openclaw_skills():
    from ..bridges.openclaw import list_skills
    return {"skills": await list_skills()}


@router.post("/openclaw/execute")
async def openclaw_execute(data: dict):
    from ..bridges.openclaw import execute_skill
    skill = data.get("skill", "")
    if not skill:
        raise HTTPException(status_code=400, detail="skill is required")
    return await execute_skill(skill, data.get("params"))

@router.get("/openclaw/agents")
async def openclaw_agents():
    from ..bridges.openclaw import list_agents
    return {"agents": await list_agents()}


@router.post("/health/repair")
async def health_repair(data: dict = None):
    from datetime import datetime, timezone

    from ..bridges.mcp import call_tool
    result = await call_tool("docker_ps", {})
    services = result if isinstance(result, dict) else {}
    return {
        "status": "repair_triggered",
        "abe_service": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services_checked": services,
    }


@router.post("/sync")
async def trigger_sync(payload: TokenPayload = Depends(require_role(Role.CEO))):
    result = await abe_service.sync.sync_now()
    abe_service.reload_data()
    return result


@router.get("/sync/status")
async def sync_status(payload: TokenPayload = Depends(require_role(Role.CEO))):
    return abe_service.sync.status()


@router.post("/health/night-cycle")
async def night_cycle_hook(data: dict):
    import json
    from datetime import datetime, timezone
    from pathlib import Path

    EVENTS_PATH = Path(__file__).resolve().parent.parent.parent.parent / "state" / "logs" / "events.jsonl"
    EVENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = json.dumps({
        "event": "night_cycle", "producer": "abe-service",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": data or {},
    })
    with open(EVENTS_PATH, "a") as f:
        f.write(entry + "\n")
    return {"status": "logged", "event": "night_cycle"}
