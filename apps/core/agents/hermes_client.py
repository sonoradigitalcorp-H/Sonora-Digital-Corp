# Re-export desde apps/act/agents/hermes_client.py
import importlib
import logging

logger = logging.getLogger(__name__)

try:
    mod = importlib.import_module("apps.act.agents.hermes_client")
    HermesClient = getattr(mod, "HermesClient")
    logger.info("HermesClient loaded from apps.act.agents")
except (ImportError, AttributeError) as e:
    logger.warning("HermesClient from apps.act.agents not available: %s", e)

    class HermesClient:
        def __init__(self, *args, **kwargs):
            pass

        async def call_tool(self, *args, **kwargs):
            return {"status": "unavailable", "error": "HermesClient not loaded"}

        async def health(self):
            return {"status": "unavailable"}

        async def list_tools(self):
            return []

        async def query_neo4j(self, *args, **kwargs):
            return []

        async def search_qdrant(self, *args, **kwargs):
            return []
