"""Continuity Router — API endpoints for cross-channel session continuity."""

from fastapi import APIRouter, HTTPException, Query
from platforms.continuity_bridge import ContinuityBridge

router = APIRouter(prefix="/api/continuity", tags=["continuity"])
bridge = ContinuityBridge()


@router.get("/{user_identifier}")
def get_continuity_context(
    user_identifier: str,
    channel: str = Query("web", description="Source channel (telegram, whatsapp, web, voice)"),
):
    """Get unified cross-channel context for a user.

    Returns session info, active channels, recent topics, pending items, and preferences.
    """
    context = bridge.get_context(user_identifier, channel)
    if not context:
        raise HTTPException(status_code=404, detail="User not found")
    return context


@router.post("/link")
def link_identities(
    primary: str,
    secondary: str,
    primary_channel: str = Query(..., description="Primary channel name"),
    secondary_channel: str = Query(..., description="Secondary channel name"),
):
    """Link two channel-specific identities as the same user.

    Example:
        POST /api/continuity/link?primary=12345&secondary=%2B521555010203&primary_channel=telegram&secondary_channel=whatsapp
    """
    success = bridge.link_identities(primary, secondary, primary_channel, secondary_channel)
    if not success:
        raise HTTPException(status_code=409, detail="Could not link identities (possibly already linked to different users)")
    unified_id = bridge.get_unified_user_id(primary, primary_channel)
    return {
        "status": "linked",
        "unified_user_id": unified_id,
        "primary": {"channel": primary_channel, "id": primary},
        "secondary": {"channel": secondary_channel, "id": secondary},
    }


@router.get("/{user_identifier}/history")
def get_history(
    user_identifier: str,
    channel: str = Query("web"),
    channels_filter: str = Query(None, alias="channels", description="Comma-separated channel filter"),
    limit: int = Query(20, ge=1, le=100),
):
    """Get recent interaction history for a user, optionally filtered by channels."""
    filter_list = channels_filter.split(",") if channels_filter else None
    history = bridge.get_recent_history(user_identifier, channel, channels_filter=filter_list, limit=limit)
    return {"user_identifier": user_identifier, "channel": channel, "count": len(history), "history": history}
