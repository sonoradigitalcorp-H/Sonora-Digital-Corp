import asyncio
import logging
from datetime import datetime, timezone

import yaml

from apps.observe.pipeline import load_registry, run_pipeline

logger = logging.getLogger(__name__)


def parse_cron_to_seconds(expr: str) -> int:
    parts = expr.strip().split()
    if len(parts) < 5:
        return 3600
    minute = parts[0]
    hour = parts[1]
    if minute == "*" and hour == "*":
        return 60
    if minute == "*" and hour != "*":
        return 3600
    if minute.startswith("*/"):
        return int(minute[2:]) * 60
    return 3600


def next_run(cron_expr: str) -> str:
    interval = parse_cron_to_seconds(cron_expr)
    return datetime.now(timezone.utc).isoformat()


class ObserveScheduler:
    def __init__(self):
        self._tasks = {}

    async def run_cycle(self) -> dict:
        logger.info("Observe scheduler cycle starting")
        registry = load_registry()
        if not registry:
            return {"status": "no_registry"}

        for platform, config in registry.get("platforms", {}).items():
            if not config.get("enabled"):
                continue
            logger.info("Pipeline triggered by schedule: %s (%s)", platform, config.get("schedule"))

        result = await run_pipeline()
        logger.info("Pipeline completed: %d collected, %d errors", result.get("collected", 0), len(result.get("errors", [])))
        return result

    async def start(self, interval: int = 1800):
        logger.info("Observe scheduler started (interval=%ds)", interval)
        while True:
            await self.run_cycle()
            await asyncio.sleep(interval)
