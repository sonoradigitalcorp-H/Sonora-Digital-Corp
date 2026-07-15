import logging

from ..bridges import neo4j as neo4j_bridge
from ..bridges.mcp import call_tool as mcp_call

log = logging.getLogger("abe.crm")


class CRM:
    async def search_artists(self, query: str = "", status: str = "") -> list[dict]:
        result = await mcp_call("abe_list_artists", {"status": status} if status else {})
        artists = result.get("artists", [])
        if query:
            q = query.lower()
            artists = [a for a in artists if q in a.get("name", "").lower()]
        return artists

    async def get_artist_kpi(self, artist_id: str) -> dict | None:
        result = await mcp_call("abe_get_artist", {"artist_id": artist_id})
        return result if "error" not in result else None

    def search_fans(self, query: str = "") -> list[dict]:
        return neo4j_bridge.search_contacts(query)

    def get_fan(self, phone: str) -> dict | None:
        try:
            from src.core.neo4j_store import get_contact
            return get_contact(phone)
        except ImportError:
            return None

    def create_fan(self, phone: str, name: str = "") -> dict | None:
        return neo4j_bridge.create_contact(phone, name, status="fan")

    def fan_summary(self) -> dict:
        return neo4j_bridge.contacts_summary()
