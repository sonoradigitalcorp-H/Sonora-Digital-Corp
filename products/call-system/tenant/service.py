import json
import os
import uuid
from datetime import datetime
import yaml

TENANTS_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "tenants.yaml")
CALLS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "calls")
os.makedirs(CALLS_PATH, exist_ok=True)


def _load_tenants():
    if not os.path.exists(TENANTS_PATH):
        return {"tenants": []}
    with open(TENANTS_PATH, "r") as f:
        return yaml.safe_load(f) or {"tenants": []}


def _save_tenants(data):
    with open(TENANTS_PATH, "w") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)


def get_tenant(tenant_id=None, phone=None, name=None):
    data = _load_tenants()
    for t in data.get("tenants", []):
        if tenant_id and t.get("id") == tenant_id:
            return t
        if phone and t.get("phone") == phone:
            return t
        if name and t.get("name", "").lower() == name.lower():
            return t
    return None


def create_tenant(name, phone="", company="", source="inbound_call", niche="general"):
    data = _load_tenants()
    tenant_id = f"tenant_{uuid.uuid4().hex[:8]}"
    tenant = {
        "id": tenant_id,
        "name": name,
        "phone": phone,
        "company": company or name,
        "tier": "lead",
        "plan": "trial",
        "lead_type": "cold",
        "niche": niche,
        "voice": "es-MX-DaliaNeural",
        "first_contact": str(datetime.utcnow().isoformat()),
        "last_call": None,
        "total_calls": 0,
        "total_duration_min": 0,
        "status": "active",
        "source": source,
        "ab_variant": "A",
        "skills": ["support"],
    }
    data.setdefault("tenants", []).append(tenant)
    _save_tenants(data)
    return tenant


def update_tenant(tenant_id, updates):
    data = _load_tenants()
    for t in data.get("tenants", []):
        if t["id"] == tenant_id:
            t.update(updates)
            _save_tenants(data)
            return t
    return None


def save_call(tenant_id, direction, duration_sec, transcript, summary, sentiment="neutral", topics=None):
    call_id = f"call_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:4]}"
    call = {
        "id": call_id,
        "tenant_id": tenant_id,
        "direction": direction,
        "started_at": datetime.utcnow().isoformat(),
        "duration_sec": duration_sec,
        "transcript": transcript,
        "summary": summary,
        "sentiment": sentiment,
        "topics": topics or [],
    }
    call_path = os.path.join(CALLS_PATH, f"{call_id}.json")
    with open(call_path, "w") as f:
        json.dump(call, f, indent=2, ensure_ascii=False)

    update_tenant(tenant_id, {
        "last_call": call["started_at"],
        "total_calls": (get_tenant(tenant_id) or {}).get("total_calls", 0) + 1,
    })
    return call


def get_call_history(tenant_id, limit=5):
    calls = []
    if os.path.exists(CALLS_PATH):
        for fname in sorted(os.listdir(CALLS_PATH), reverse=True):
            if fname.endswith(".json"):
                with open(os.path.join(CALLS_PATH, fname)) as f:
                    call = json.load(f)
                    if call.get("tenant_id") == tenant_id:
                        calls.append(call)
                        if len(calls) >= limit:
                            break
    return calls


def get_lead_type(tenant):
    plan = tenant.get("plan", "trial")
    total_calls = tenant.get("total_calls", 0)
    source = tenant.get("source", "inbound_call")
    tier = tenant.get("tier", "lead")

    if tier in ("master", "enterprise"):
        return "hot"
    if plan in ("pro", "enterprise") and total_calls > 5:
        return "hot"
    if plan == "trial" and total_calls > 2:
        return "warm"
    if tier == "lead" and source == "campaign":
        return "cold"
    return "cold"
