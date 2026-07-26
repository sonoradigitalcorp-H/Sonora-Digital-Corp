"""manage-crm handler — HAS-005
Manage artist CRM: contacts, leads, follow-ups, relationship tracking, opportunity pipeline.
"""
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent.parent.parent
CRM_DIR = REPO / "state" / "crm"


def _ensure_dir():
    CRM_DIR.mkdir(parents=True, exist_ok=True)


def _contacts_path() -> Path:
    return CRM_DIR / "contacts.json"


def _leads_path() -> Path:
    return CRM_DIR / "leads.json"


def _load_json(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, Exception):
        return []


def _save_json(path: Path, data: list[dict]):
    path.write_text(json.dumps(data, indent=2, default=str))


async def execute(context: Any) -> dict:
    _ensure_dir()
    input_data = context if isinstance(context, dict) else {}
    action = input_data.get("action", "list")
    contacts = _load_json(_contacts_path())
    leads = _load_json(_leads_path())

    if action == "add_contact":
        contact = {
            "id": str(uuid.uuid4()),
            "name": input_data.get("name", ""),
            "email": input_data.get("email", ""),
            "phone": input_data.get("phone", ""),
            "artist_id": input_data.get("artist_id", ""),
            "role": input_data.get("role", "artist"),
            "notes": input_data.get("notes", ""),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        contacts.append(contact)
        _save_json(_contacts_path(), contacts)
        return {"action": "add_contact", "contact": contact, "total_contacts": len(contacts)}

    elif action == "add_lead":
        lead = {
            "id": str(uuid.uuid4()),
            "name": input_data.get("name", ""),
            "artist_name": input_data.get("artist_name", ""),
            "score": input_data.get("score", 0),
            "status": input_data.get("status", "new"),
            "source": input_data.get("source", "manual"),
            "estimated_revenue": input_data.get("estimated_revenue", 0),
            "notes": input_data.get("notes", ""),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        leads.append(lead)
        _save_json(_leads_path(), leads)
        return {"action": "add_lead", "lead": lead, "total_leads": len(leads)}

    elif action == "update_lead":
        lead_id = input_data.get("lead_id", "")
        updates = {k: v for k, v in input_data.items() if k not in ("action", "lead_id")}
        for lead in leads:
            if lead.get("id") == lead_id:
                lead.update(updates)
                lead["updated_at"] = datetime.now(timezone.utc).isoformat()
                _save_json(_leads_path(), leads)
                return {"action": "update_lead", "lead": lead}
        return {"action": "update_lead", "error": f"Lead {lead_id} not found"}

    elif action == "list_contacts":
        return {"action": "list_contacts", "contacts": contacts, "total": len(contacts)}

    elif action == "list_leads":
        status_filter = input_data.get("status", "")
        filtered = [l for l in leads if l.get("status") == status_filter] if status_filter else leads
        return {"action": "list_leads", "leads": filtered, "total": len(filtered)}

    return {"action": action, "contacts": len(contacts), "leads": len(leads)}
