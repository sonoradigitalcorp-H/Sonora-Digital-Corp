"""
Agent-to-Agent Communication Protocol
Hermes ↔ OpenClaw ↔ JARVIS ↔ n8n ↔ Telegram
"""
import json, logging, httpx, asyncio
from datetime import datetime

log = logging.getLogger("agents.communicator")

AGENTS = {
    "hermes": {"url": "http://localhost:8000", "type": "api"},
    "openclaw": {"url": "http://localhost:18789", "type": "mcp"},
    "jarvis": {"url": "http://localhost:8000", "type": "api"},
    "n8n": {"url": "http://localhost:5678", "type": "webhook"},
    "telegram": {"token": "8875376383:AAG4dDoxdUfHqR7oIqW0lC4ygLxfzfg1EMA", "type": "bot"},
}

class AgentOrchestrator:
    def __init__(self):
        self.conversations = []
        self.log = []
    
    async def tell(self, from_agent: str, to_agent: str, message: str):
        entry = {
            "from": from_agent, "to": to_agent,
            "message": message, "timestamp": datetime.now().isoformat()
        }
        self.conversations.append(entry)
        self.log.append(f"[{from_agent}→{to_agent}] {message[:80]}")
        
        if to_agent == "telegram":
            async with httpx.AsyncClient() as c:
                await c.post(
                    f"https://api.telegram.org/bot{AGENTS['telegram']['token']}/sendMessage",
                    json={"chat_id": "526621234567", "text": f"*{from_agent}:* {message}", "parse_mode": "Markdown"}
                )
        return entry
    
    async def broadcast(self, from_agent: str, message: str):
        for agent in AGENTS:
            if agent != from_agent:
                await self.tell(from_agent, agent, message)
    
    def get_conversation_log(self) -> str:
        return "\n".join(self.log[-20:])

# Singleton
_orchestrator = None
def get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
    return _orchestrator
