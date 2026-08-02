"""crm handler — CRM
Gestión de leads, clientes y pipeline.
"""
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent.parent.parent
STORE_PATH = REPO / "state" / "crm" / "leads.json"


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

    if action == "add_lead":
        lead = {
            "id": str(uuid.uuid4()),
            "name": input_data.get("name", ""),
            "contact": input_data.get("contact", ""),
            "source": input_data.get("source", "web"),
            "notes": input_data.get("notes", ""),
            "score": input_data.get("score", 0),
            "status": "new",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        leads = _load()
        leads.append(lead)
        _save(leads)
        return {"action": "add_lead", "lead": lead, "total": len(leads)}

    elif action == "score":
        lead_id = input_data.get("lead_id", "")
        score = input_data.get("score", 0)
        leads = _load()
        for lead in leads:
            if lead["id"] == lead_id:
                lead["score"] = score
                lead["status"] = "qualified" if score >= 7 else "nurturing"
                lead["updated_at"] = datetime.now(timezone.utc).isoformat()
                _save(leads)
                return {"action": "score", "lead": lead}
        return {"action": "score", "error": "Lead not found"}

    elif action == "search":
        query = input_data.get("query", "").lower()
        leads = _load()
        results = [l for l in leads if query in l["name"].lower() or query in l["contact"].lower()]
        return {"action": "search", "query": query, "results": results, "total": len(results)}

    elif action == "list":
        leads = _load()
        status_filter = input_data.get("status", "")
        if status_filter:
            leads = [l for l in leads if l["status"] == status_filter]
        return {"action": "list", "leads": leads, "total": len(leads)}

    return {"action": action, "leads": len(_load())}
