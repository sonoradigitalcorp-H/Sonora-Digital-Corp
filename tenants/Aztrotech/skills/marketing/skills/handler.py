"""marketing handler — Marketing Campaigns
Creación y lanzamiento de campañas.
"""
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent.parent.parent
STORE_PATH = REPO / "state" / "marketing" / "campaigns.json"


def _ensure():
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not STORE_PATH.exists():
        STORE_PATH.write_text("[]")


def _load() -> list[dict]:
    _ensure()
    return json.loads(STORE_PATH.read_text())


def _save(data: list[dict]):
    _ensure()
    STORE_PATH.write_text(json.dumps(data, indent=2, default=str))


async def execute(context: Any) -> dict:
    input_data = context if isinstance(context, dict) else {}
    action = input_data.get("action", "list")

    if action == "create":
        campaign = {
            "id": str(uuid.uuid4()),
            "name": input_data.get("name", ""),
            "segment": input_data.get("segment", "general"),
            "message": input_data.get("message", ""),
            "channel": input_data.get("channel", "whatsapp"),
            "status": "draft",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        campaigns = _load()
        campaigns.append(campaign)
        _save(campaigns)
        return {"action": "create", "campaign": campaign, "total": len(campaigns)}

    elif action == "launch":
        campaign_id = input_data.get("campaign_id", "")
        campaigns = _load()
        for c in campaigns:
            if c["id"] == campaign_id:
                c["status"] = "active"
                c["launched_at"] = datetime.now(timezone.utc).isoformat()
                _save(campaigns)
                return {"action": "launch", "campaign": c}
        return {"action": "launch", "error": "Campaign not found"}

    elif action == "list":
        campaigns = _load()
        status_filter = input_data.get("status", "")
        if status_filter:
            campaigns = [c for c in campaigns if c["status"] == status_filter]
        return {"action": "list", "campaigns": campaigns, "total": len(campaigns)}

    return {"action": action, "campaigns": len(_load())}
