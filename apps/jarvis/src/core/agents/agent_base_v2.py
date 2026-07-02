"""AgentBaseV2 — Nueva base para agentes JARVIS con Redis + Ollama + HermesClient.

Cada agente ahora:
1. Se comunica via Redis Stream (agent:messages)
2. Usa modelo local Ollama para decisiones (ask_local)
3. Llama herramientas via HermesClient
4. Guarda decisiones en Memory MCP
"""
import json
import logging
from datetime import datetime, timezone
from typing import Any

# Redis
REDIS_STREAM = "agent:messages"
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_PASS = "sdc2026prod"

# Hermes
from apps.agents.hermes_client import HermesClient

# Ollama
from apps.jarvis.src.core.llm import ask_local


def publish_to_redis(event_type: str, agent: str, data: dict):
    """Publish event to Redis Stream."""
    try:
        import redis as redis_lib
        r = redis_lib.Redis(
            host=REDIS_HOST, port=REDIS_PORT, db=0,
            password=REDIS_PASS, decode_responses=True, socket_timeout=3,
        )
        payload = {
            "type": event_type,
            "agent": agent,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        payload.update(data)
        r.xadd(REDIS_STREAM, payload, maxlen=1000)
        r.close()
    except Exception as e:
        logging.getLogger("agent.base").warning(f"Redis publish failed: {e}")


def ask_ollama(prompt: str, model: str = "qwen3:4b-64k") -> str:
    """Ask local Ollama model. Returns response text."""
    try:
        return ask_local(prompt, model=model) or ""
    except Exception as e:
        return f"Error: {e}"


class AgentBaseV2:
    """Base class for all V2 agents with Redis + Ollama + HermesClient."""

    name: str = "base"
    description: str = "Base V2 agent"
    timeout: int = 30

    def __init__(self):
        self.log = logging.getLogger(f"jarvis.agent.v2.{self.name}")
        self.hermes = HermesClient()

    async def run(self, task: str, context: dict = None) -> dict[str, Any]:
        raise NotImplementedError

    def publish(self, event_type: str, **data):
        """Publish event to Redis Stream."""
        publish_to_redis(event_type, self.name, data)

    def think(self, prompt: str) -> str:
        """Use local Ollama to reason about something."""
        return ask_ollama(prompt)

    async def neo4j_query(self, cypher: str) -> dict:
        """Query Neo4j via Hermes."""
        return await self.hermes.query_neo4j(cypher)

    async def qdrant_search(self, collection: str, vector: list[float], limit: int = 5) -> dict:
        """Search Qdrant via Hermes."""
        return await self.hermes.search_qdrant(collection, vector, limit)

    async def health(self) -> dict:
        """Check system health via Hermes."""
        return await self.hermes.health_status()

    def success(self, task: str, **extra) -> dict:
        return {"agent": self.name, "task": task, "status": "success", "v2": True, **extra}

    def error(self, task: str, error: str, **extra) -> dict:
        return {"agent": self.name, "task": task, "status": "error", "error": error, "v2": True, **extra}

    def __repr__(self) -> str:
        return f"<AgentV2 {self.name}>"
