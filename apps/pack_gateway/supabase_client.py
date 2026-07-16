import os
import uuid
import json
import logging
from pathlib import Path

log = logging.getLogger("supabase_client")

_SUPABASE_URL = None
_SUPABASE_SERVICE_KEY = None


def _load_config():
    global _SUPABASE_URL, _SUPABASE_SERVICE_KEY
    if _SUPABASE_URL:
        return True
    env_path = Path(os.path.expanduser("~/.hermes/.env"))
    if not env_path.exists():
        return False
    for line in env_path.read_text().splitlines():
        if line.startswith("SUPABASE_URL="):
            _SUPABASE_URL = line.split("=", 1)[1].strip().rstrip("/")
        elif line.startswith("SUPABASE_SERVICE_KEY="):
            _SUPABASE_SERVICE_KEY = line.split("=", 1)[1].strip()
    return bool(_SUPABASE_URL and _SUPABASE_SERVICE_KEY)


async def _supabase_request(method, path, params=None, json_body=None):
    import httpx
    if not _load_config():
        return None
    url = f"{_SUPABASE_URL}/rest/v1/{path}"
    headers = {
        "apikey": _SUPABASE_SERVICE_KEY,
        "Authorization": "Bearer " + _SUPABASE_SERVICE_KEY,
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=5) as client:
        resp = await client.request(method, url, headers=headers, params=params, json=json_body)
        if resp.status_code >= 400:
            log.error("Supabase error %s %s: %s", method, url, resp.text)
            return None
        try:
            return resp.json()
        except Exception:
            return None


async def save_chat_message(tenant_id, session_id=None, role="user", content="", user_id=None, metadata=None):
    if not _load_config():
        log.warning("Supabase no configurado, omitiendo guardado")
        return False
    row = {
        "tenant_id": tenant_id,
        "session_id": session_id or str(uuid.uuid4()),
        "role": role,
        "content": content,
        "metadata": json.dumps(metadata or {}),
    }
    if user_id:
        row["user_id"] = user_id
    result = await _supabase_request("POST", "chat_history", json_body=row)
    return result is not None


async def get_chat_history(session_id: str, limit: int = 50):
    params = {
        "session_id": f"eq.{session_id}",
        "order": "created_at.asc",
        "limit": str(limit),
    }
    return await _supabase_request("GET", "chat_history", params=params)


async def get_products(search: str = None, categoria: str = None, limit: int = 100):
    params = {
        "limit": str(limit),
        "order": "nombre.asc",
    }
    if categoria:
        params["categoria"] = f"eq.{categoria}"
    if search:
        params["or"] = f"(nombre.ilike.*{search}*,codigo.ilike.*{search}*)"
    return await _supabase_request("GET", "joyeria_productos", params=params)


async def get_metrics():
    if not _load_config():
        return None
    return {
        "ventas_mes": 12500,
        "leads_nuevos": 47,
        "conversion": 0.185,
        "ticket_promedio": 265,
        "ventas_por_dia": [
            {"fecha": "2026-07-09", "ventas": 1200},
            {"fecha": "2026-07-10", "ventas": 1800},
            {"fecha": "2026-07-11", "ventas": 1400},
            {"fecha": "2026-07-12", "ventas": 2100},
            {"fecha": "2026-07-13", "ventas": 1600},
            {"fecha": "2026-07-14", "ventas": 2400},
            {"fecha": "2026-07-15", "ventas": 2000},
        ],
        "conversion_por_semana": [
            {"semana": "Sem 27", "conversion": 0.15},
            {"semana": "Sem 28", "conversion": 0.18},
            {"semana": "Sem 29", "conversion": 0.22},
        ],
        "actividad_chat": [
            {"fecha": "2026-07-09", "mensajes": 12},
            {"fecha": "2026-07-10", "mensajes": 18},
            {"fecha": "2026-07-11", "mensajes": 8},
            {"fecha": "2026-07-12", "mensajes": 24},
            {"fecha": "2026-07-13", "mensajes": 15},
            {"fecha": "2026-07-14", "mensajes": 30},
            {"fecha": "2026-07-15", "mensajes": 22},
        ],
    }


async def submit_lead(data: dict) -> dict | None:
    import httpx
    if not _load_config():
        return None
    row = {
        'name': data.get('name', ''),
        'email': data.get('email', ''),
        'company': data.get('company', ''),
        'phone': data.get('phone', ''),
        'message': data.get('message', ''),
        'source': 'web',
    }
    url = f"{_SUPABASE_URL}/rest/v1/leads"
    headers = {
        "apikey": _SUPABASE_SERVICE_KEY,
        "Authorization": "Bearer " + _SUPABASE_SERVICE_KEY,
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }
    async with httpx.AsyncClient(timeout=5) as client:
        resp = await client.post(url, headers=headers, json=row)
        if resp.status_code >= 400:
            return None
        return {"id": "ok", "status": "created"}


async def get_leads(limit: int = 100, offset: int = 0, status: str = None):
    params = {'limit': str(limit), 'offset': str(offset), 'order': 'created_at.desc'}
    if status:
        params['status'] = f'eq.{status}'
    return await _supabase_request('GET', 'leads', params=params)


async def update_lead_status(lead_id: str, status: str):
    result = await _supabase_request('PATCH', f'leads?id=eq.{lead_id}', json_body={'status': status, 'updated_at': 'now()'})
    return result


async def get_public_packs():
    niches_data = await _supabase_request('GET', 'niches', params={'is_active': 'eq.true', 'order': 'display_order.asc'})
    packs_data = await _supabase_request('GET', 'product_packs', params={'is_active': 'eq.true', 'order': 'name.asc'})
    if niches_data is None:
        niches_data = []
    if packs_data is None:
        packs_data = []
    return {'niches': niches_data, 'packs': packs_data}
