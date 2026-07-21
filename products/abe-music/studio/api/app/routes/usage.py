from fastapi import APIRouter, Header
from app.db import check_tier_limit, TIER_LIMITS

router = APIRouter()

@router.get("/studio/usage")
async def get_usage(x_tier: str = Header("free"), x_user_id: str = Header("0")):
    user_id = int(x_user_id)
    tier_cfg = TIER_LIMITS.get(x_tier, TIER_LIMITS["free"])
    limit = check_tier_limit(user_id, x_tier)
    return {
        **limit,
        "features": {
            "watermark": tier_cfg["watermark"],
            "audio_sync": tier_cfg["audio_sync"],
            "clone_studio": tier_cfg["clone_studio"],
            "max_resolution": tier_cfg["max_resolution"]
        }
    }

@router.get("/studio/tiers")
async def list_tiers():
    return {
        "tiers": list(TIER_LIMITS.keys()),
        "details": {k: {**v, "reels": "ilimitado" if v["reels"] == -1 else v["reels"]} for k, v in TIER_LIMITS.items()}
    }
