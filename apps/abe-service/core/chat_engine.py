import logging
import uuid
from typing import Any

from ..bridges import engram as engram_bridge
from ..bridges import neo4j as neo4j_bridge
from ..bridges.mcp import call_tool as mcp_call
from .rag_engine import RAGEngine

log = logging.getLogger("abe.chat")


class ChatEngine:
    def __init__(self, rag: RAGEngine):
        self.rag = rag

    async def process(
        self,
        text: str,
        session_id: str | None = None,
        context: dict | None = None,
    ) -> dict[str, Any]:
        ctx = context or {}
        if not session_id:
            session_id = f"abe_{uuid.uuid4().hex[:12]}"
            neo4j_bridge.create_session(session_id, title=f"Chat: {text[:40]}")

        engram_results = engram_bridge.query(text, limit=3)
        rag_results = self.rag.search(text, limit=3)

        enriched = {
            "text": text,
            "session_id": session_id,
            "role": ctx.get("role", "artista"),
            "engram_context": engram_results,
            "rag_context": rag_results,
            "user_id": ctx.get("user_id", "anonymous"),
        }

        intent = self._classify(text)
        response = await self._route(intent, enriched)
        response_text = response.get("text", response.get("result", response.get("error", "OK")))

        neo4j_bridge.add_message(session_id, "user", text)
        neo4j_bridge.add_message(session_id, "assistant", str(response_text)[:1000])

        engram_bridge.store(
            f"chat-{session_id}",
            "abe-chat",
            text[:200],
            f"User asked: {text[:200]}\nResponse: {str(response_text)[:200]}",
            importance="medium",
            layer="project",
        )

        return {
            "text": response_text,
            "session_id": session_id,
            "intent": intent,
            "source": response.get("source", "local"),
        }

    def _classify(self, text: str) -> str:
        t = text.lower()
        if any(w in t for w in ["stream", "reproducci", "oyente"]):
            return "streams"
        if any(w in t for w in ["revenue", "ingreso", "dinero", "pago"]):
            return "revenue"
        if any(w in t for w in ["contrato", "acuerdo", "firmar", "legal"]):
            return "contract"
        if any(w in t for w in ["lanzamient", "release", "canci", "tema", "album"]):
            return "release"
        if any(w in t for w in ["artista", "nuevo", "firm"]):
            return "artist"
        if any(w in t for w in ["report", "dashboard", "kpi", "ceo"]):
            return "dashboard"
        if any(w in t for w in ["distribuci", "oplaai", "platform"]):
            return "distribution"
        if any(w in t for w in ["fan", "seguidor", "contacto"]):
            return "fan"
        return "general"

    async def _route(self, intent: str, enriched: dict) -> dict[str, Any]:
        tool_map = {
            "streams": "abe_record_stream",
            "revenue": "abe_record_revenue",
            "dashboard": "abe_ceo_dashboard",
            "contract": None,
            "release": None,
            "artist": None,
            "distribution": None,
            "fan": None,
            "general": None,
        }

        tool = tool_map.get(intent)
        if tool:
            result = await mcp_call(tool, enriched)
            return {**result, "source": "mcp"}

        return {
            "text": f"Clasificado como: {intent}. Procesaré tu solicitud en breve.",
            "intent": intent,
            "source": "local",
        }
