import logging
from datetime import datetime, timezone
from typing import Any

import httpx

from products.mystik.config import config

logger = logging.getLogger(__name__)


class TwentyCRM:
    def __init__(self):
        self.base_url = config.twenty_api_url
        self.api_key = config.twenty_api_key

    def _headers(self) -> dict:
        h = {"Content-Type": "application/json"}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    def create_lead(self, data: dict) -> dict:
        lead = {
            "name": data.get("name", ""),
            "email": data.get("email", ""),
            "company": data.get("company", ""),
            "phone": data.get("phone", ""),
            "source": data.get("source", "mystik-web"),
            "tenant": data.get("tenant", "sonora"),
            "stage": "new",
            "score": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        try:
            resp = httpx.post(
                f"{self.base_url}/graphql",
                json={"query": """
                    mutation CreateLead($data: LeadCreateInput!) {
                        createLead(data: $data) { id name email stage score }
                    }
                """, "variables": {"data": lead}},
                headers=self._headers(), timeout=10,
            )
            if resp.status_code == 200:
                result = resp.json()
                return result.get("data", {}).get("createLead", lead)
            logger.warning("Twenty CRM returned %s, using local fallback", resp.status_code)
        except Exception as e:
            logger.warning("Twenty CRM unavailable: %s, using local fallback", e)
        return {**lead, "id": f"local-{hash(lead['email'])}"}

    def list_leads(self, tenant: str = "sonora") -> list[dict]:
        try:
            resp = httpx.post(
                f"{self.base_url}/graphql",
                json={"query": "{ leads { id name email stage score company source } }"},
                headers=self._headers(), timeout=10,
            )
            if resp.status_code == 200:
                return resp.json().get("data", {}).get("leads", [])
        except Exception:
            pass
        return []

    def qualify(self, lead_id: str, tenant: str = "sonora") -> dict:
        score = 50
        stage = "qualified"
        try:
            resp = httpx.post(
                f"{self.base_url}/graphql",
                json={"query": """
                    mutation UpdateLead($id: ID!, $data: LeadUpdateInput!) {
                        updateLead(id: $id, data: $data) { id stage score }
                    }
                """, "variables": {"id": lead_id, "data": {"stage": stage, "score": score}}},
                headers=self._headers(), timeout=10,
            )
            if resp.status_code == 200:
                return resp.json().get("data", {}).get("updateLead", {})
        except Exception:
            pass
        return {"id": lead_id, "stage": stage, "score": score}
