"""Pipeline Bridge — Connects SPEC pipeline completions to Engram memory."""

import logging
from pathlib import Path
from typing import Optional

from src.core.engram import engram

log = logging.getLogger(__name__)

COMPLETED_DIR = Path("process/completed")


def store_spec_completion(
    spec_id: str,
    summary: str,
    tags: Optional[list[str]] = None,
) -> bool:
    """Store a SPEC completion into Engram memory.

    :param spec_id: Unique spec identifier (e.g. SPEC-20260701-001)
    :param summary: Short description of what was completed
    :param tags: Optional list of tag strings for search
    :return: True if stored successfully, False on error or empty spec_id
    """
    if not spec_id:
        return False
    try:
        engram.store_learning(
            spec_id=spec_id,
            tag="pipeline",
            summary=summary,
            context=f"Pipeline completion: {spec_id}",
            importance="high",
            layer="project",
        )
        return True
    except Exception as e:
        log.warning("store_spec_completion failed for %s: %s", spec_id, e)
        return False


def query_engram_context(task: str, limit: int = 10) -> list[dict]:
    """Query Engram for memories relevant to a task description.

    :param task: Natural-language task description
    :param limit: Maximum number of results
    :return: List of memory dicts (keys: spec_id, summary, context, ...)
    """
    try:
        return engram.query_context(task, limit=limit)
    except Exception as e:
        log.warning("query_engram_context failed: %s", e)
        return []


def format_engram_context(results: list[dict]) -> str:
    """Format engram query results into a human-readable context string.

    :param results: List of memory dicts from query_engram_context
    :return: Formatted string with spec references, or empty string
    """
    if not results:
        return ""
    lines = ["\n--- Relevant past learnings ---"]
    for r in results:
        lines.append(f"  [{r.get('spec_id', '?')}] {r.get('summary', '')}")
        if r.get("context"):
            lines.append(f"    Context: {r['context']}")
    lines.append("---\n")
    return "\n".join(lines)


def scan_and_store_pipeline() -> int:
    """Scan process/completed/ and store any unregistered completions.

    :return: Number of new completions stored
    """
    if not COMPLETED_DIR.exists():
        return 0
    stored = 0
    for entry in sorted(COMPLETED_DIR.iterdir()):
        if entry.is_dir() and entry.name.startswith("SPEC-"):
            spec_id = entry.name
            summary = f"Pipeline completion for {spec_id}"
            try:
                if store_spec_completion(spec_id, summary):
                    stored += 1
            except Exception as e:
                log.warning("scan_and_store: error processing %s: %s", spec_id, e)
    return stored
