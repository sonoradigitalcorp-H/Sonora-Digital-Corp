import logging
import uuid
from typing import Any

from ..bridges import engram as engram_bridge
from ..bridges import neo4j as neo4j_bridge
from ..bridges.mcp import call_tool as mcp_call
from .rag_engine import RAGEngine

# Import OpenCode bridge for LLM-powered responses
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
        rag_results = await self.rag.search(text, limit=3)

        enriched = {
            "text": text,
            "session_id": session_id,
            "role": ctx.get("role", "artista"),
            "engram_context": engram_results,
            "rag_context": rag_results,
            "user_id": ctx.get("user_id", "anonymous"),
        }

        intent = self._classify(text)

        # Route CRM/revenue intents to MCP tools, everything else to LLM MCP
        tool_map = {
            "streams": "abe_record_stream",
            "revenue": "abe_record_revenue",
            "dashboard": "abe_ceo_dashboard",
        }
        tool = tool_map.get(intent)
        if tool:
            response = await mcp_call(tool, enriched)
            response_text = response.get("text", response.get("result", "OK"))
            source = "mcp"
        else:
            # Use LLM MCP for general queries
            tenant = ctx.get("tenant", "sonora")
            system_prompt = self._system_prompt_for_tenant(tenant)
            llm_result = await mcp_call(
                "llm_complete",
                {
                    "prompt": text,
                    "system": system_prompt,
                },
            )
            if isinstance(llm_result, str):
                try:
                    llm_result = json.loads(llm_result)
                except json.JSONDecodeError:
                    llm_result = {"text": llm_result}
            # Gateway may wrap the tool output under "result"
            if "result" in llm_result and isinstance(llm_result["result"], dict):
                llm_result = llm_result["result"]
            response_text = llm_result.get("text", "No pude generar una respuesta.")
            source = "llm_mcp"

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
            "source": source,
        }

    def _system_prompt_for_tenant(self, tenant: str) -> str:
        if tenant == "abe":
            return (
                "Eres Abe, el asistente oficial de ABE Music Group. "
                "Ayudas a artistas y músicos con su carrera, distribución, revenue y comunidad. "
                "Responde en español, con tono cercano y profesional. "
                "Si no sabes algo, di que un humano del equipo ABE puede contactarlo."
            )
        return (
            "Eres Sona, el asistente oficial de Sonora Digital Corp. "
            "Ayudas a empresas a entender y contratar servicios de IA: clonación de voz, "
            "clonación de imagen, voice agents 24/7 y consultoría. "
            "Responde en español, con tono profesional y vendedor. "
            "Si el usuario quiere una demo o más información, ofrécele agendar una llamada."
        )

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
