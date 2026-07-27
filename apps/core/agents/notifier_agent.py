import importlib
import logging

logger = logging.getLogger(__name__)

try:
    mod = importlib.import_module("apps.act.agents.notifier_agent")
    send_telegram = getattr(mod, "send_telegram")
    logger.info("notifier_agent loaded from apps.act.agents")
except (ImportError, AttributeError) as e:
    logger.warning("notifier_agent from apps.act.agents not available: %s", e)

    async def send_telegram(message: str):
        return {"status": "unavailable", "error": "notifier_agent not loaded"}
