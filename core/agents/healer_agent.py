import importlib
import logging

logger = logging.getLogger(__name__)

try:
    mod = importlib.import_module("apps.act.agents.healer_agent")
    get_dependencies = getattr(mod, "get_dependencies")
    logger.info("healer_agent loaded from apps.act.agents")
except (ImportError, AttributeError) as e:
    logger.warning("healer_agent from apps.act.agents not available: %s", e)

    async def get_dependencies(service_name: str):
        return []
