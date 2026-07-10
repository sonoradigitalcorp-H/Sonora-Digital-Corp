import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path

from apps.learn.heuristics import extract_heuristics, update_truth_learned

logger = logging.getLogger(__name__)


async def run_learning_cycle() -> dict:
    logger.info("Learning cycle starting")
    heuristics = extract_heuristics()
    logger.info("Extracted %d heuristics from LECCION.md files", len(heuristics))

    result = update_truth_learned(heuristics)
    logger.info("Truth learned updated: %s", result.get("status"))

    return {
        "status": "completed",
        "heuristics_found": len(heuristics),
        "update_result": result,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


async def run_evolution_cycle() -> dict:
    try:
        from evolution.main import run_evolution
        result = await run_evolution()
        logger.info("Evolution cycle completed")
        return result
    except ImportError:
        logger.warning("evolution.main not found, skipping evolution cycle")
        return {"status": "skipped", "reason": "evolution.main not available"}
    except Exception as e:
        logger.error("Evolution cycle failed: %s", e)
        return {"status": "failed", "error": str(e)}
