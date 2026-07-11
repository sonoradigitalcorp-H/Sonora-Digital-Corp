import logging
from datetime import datetime, timezone

import httpx

from products.mystik.config import config

logger = logging.getLogger(__name__)


class ABECRM:
    def __init__(self):
        self.base_url = config.abe_crm_url

    def create_lead(self, data: dict) -> dict:
        now = datetime.now(timezone.utc).isoformat()
        lead = {
            "name": data.get("name", ""),
            "email": data.get("email", ""),
            "company": data.get("company", ""),
            "phone": data.get("phone", ""),
            "source": data.get("source", "mystik-web"),
            "tenant": data.get("tenant", "sonora"),
            "stage": "new",
            "score": 0,
            "created_at": now,
        }
        try:
            resp = httpx.post(
                f"{self.base_url}/api/leads",
                json=lead, timeout=10,
            )
            if resp.status_code in (200, 201):
                return resp.json()
            logger.warning("ABE CRM returned %s, using local fallback", resp.status_code)
        except Exception as e:
            logger.warning("ABE CRM unavailable: %s, using local fallback", e)
        return {**lead, "id": f"local-{hash(data.get('email',''))}"}

    def list_leads(self, tenant: str = "sonora") -> list[dict]:
        try:
            resp = httpx.get(f"{self.base_url}/api/leads", timeout=10)
            if resp.status_code == 200:
                return resp.json().get("leads", resp.json())
        except Exception:
            pass
        return []

    def qualify(self, lead_id: str, tenant: str = "sonora") -> dict:
        try:
            resp = httpx.post(
                f"{self.base_url}/api/leads/{lead_id}/qualify",
                json={"score": 50, "stage": "qualified", "tenant": tenant},
                timeout=10,
            )
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return {"id": lead_id, "stage": "qualified"}


# Use ABE CRM by default, switch to Twenty when ready
CRM = ABECRM
