from fastapi import APIRouter, HTTPException
from src.core.gamification import get_engine as get_gamification_engine
from src.core.mysticverse import DigitalTwinPipeline, KYCManager, TelegramBotManager

router = APIRouter()

_twins = DigitalTwinPipeline()
_bots = TelegramBotManager()
_kyc = KYCManager()


@router.post("/api/mysticverse/twin")
async def mv_create_twin(data: dict):
    return _twins.create(data)


@router.get("/api/mysticverse/twin/{twin_id}")
async def mv_get_twin(twin_id: str):
    twin = _twins.get(twin_id)
    if not twin:
        raise HTTPException(status_code=404, detail="Twin not found")
    return twin


@router.post("/api/mysticverse/kyc/age")
async def mv_kyc_age(data: dict):
    return _kyc.verify_age(data.get("creator_id", ""), data)


@router.post("/api/mysticverse/kyc/identity/{record_id}")
async def mv_kyc_identity(record_id: str, data: dict):
    return _kyc.verify_identity(record_id, data)


@router.post("/api/mysticverse/kyc/consent/{record_id}")
async def mv_kyc_consent(record_id: str, data: dict):
    return _kyc.sign_consent(record_id, data.get("signature", ""))


@router.get("/api/mysticverse/kyc/status/{creator_id}")
async def mv_kyc_status(creator_id: str):
    return {"verified": _kyc.is_verified(creator_id)}


@router.post("/api/mysticverse/gamification/xp")
async def mv_gamification_xp(data: dict):
    engine = get_gamification_engine()
    return engine.add_xp(
        data.get("player_id", ""), data.get("amount", 0), data.get("reason", "")
    )


@router.post("/api/mysticverse/gamification/action")
async def mv_gamification_action(data: dict):
    engine = get_gamification_engine()
    return engine.track_action(data.get("player_id", ""), data.get("action", ""))


@router.post("/api/mysticverse/gamification/login")
async def mv_gamification_login(data: dict):
    return get_gamification_engine().daily_login(data.get("player_id", ""))


@router.get("/api/mysticverse/gamification/player/{player_id}")
async def mv_gamification_player(player_id: str):
    engine = get_gamification_engine()
    player = engine.get_player(player_id) or engine.get_or_create_player(player_id)
    return player


@router.get("/api/mysticverse/gamification/leaderboard")
async def mv_gamification_leaderboard(limit: int = 10):
    return {"leaderboard": get_gamification_engine().get_leaderboard(limit)}


@router.get("/api/mysticverse/gamification/badges/{player_id}")
async def mv_gamification_badges(player_id: str):
    return {"badges": get_gamification_engine().get_all_badges(player_id)}
