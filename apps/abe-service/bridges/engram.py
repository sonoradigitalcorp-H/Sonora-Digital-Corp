import logging
from typing import Any

log = logging.getLogger("abe.bridge.engram")


def _get_engram():
    try:
        from src.core.engram import engram
        return engram
    except ImportError:
        log.warning("engram not available")
        return None


def store(spec_id: str, tag: str, summary: str, context: str, importance: str = "medium", layer: str = "project"):
    e = _get_engram()
    if e:
        try:
            e.store_learning(spec_id, tag, summary, context, importance, layer)
        except Exception as ex:
            log.warning(f"Engram store error: {ex}")


def query(query: str, limit: int = 5) -> list[dict[str, Any]]:
    e = _get_engram()
    if e:
        try:
            return e.query_context(query, limit)
        except Exception as ex:
            log.warning(f"Engram query error: {ex}")
    return []
