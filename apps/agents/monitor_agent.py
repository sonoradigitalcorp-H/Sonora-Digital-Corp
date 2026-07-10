import importlib
import logging

logger = logging.getLogger(__name__)

try:
    mod = importlib.import_module("apps.act.agents.monitor_agent")
    detect_dead_containers = getattr(mod, "detect_dead_containers")
    logger.info("monitor_agent loaded from apps.act.agents")
except (ImportError, AttributeError) as e:
    logger.warning("monitor_agent from apps.act.agents not available: %s", e)

    async def detect_dead_containers():
        return []
