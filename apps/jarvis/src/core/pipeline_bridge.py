"""
Pipeline Bridge — Connects the process pipeline system to Engram memory.
Auto-stores learning on spec completion, auto-queries context before execution.
"""

import json
import logging
import os
from datetime import timezone
from typing import Any

from src.core.engram import engram

log = logging.getLogger("jarvis.pipeline_bridge")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
PROCESS_DIR = os.path.join(BASE_DIR, "process")
EVENTS_FILE = os.path.join(BASE_DIR, "state", "logs", "events.jsonl")


def _emit_event(event: str, payload: dict):
    os.makedirs(os.path.dirname(EVENTS_FILE), exist_ok=True)
    from datetime import datetime
    entry = json.dumps({
        "event": event,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    })
    try:
        with open(EVENTS_FILE, "a") as f:
            f.write(entry + "\n")
    except OSError:
        pass


def store_spec_completion(spec_id: str, summary: str, tags: list[str] = None):
    """Auto-store learning when a spec is completed."""
    if not spec_id:
        return False
    engram.store_learning(
        spec_id=spec_id,
        tag=",".join(tags or ["spec", "completed"]),
        summary=summary,
        context=f"Spec completed: {spec_id}",
        importance="high",
    )
    _emit_event("knowledge_stored", {
        "spec_id": spec_id,
        "type": "spec_completion",
        "tags": tags or [],
    })
    log.info(f"Engram: stored completion for {spec_id}")
    return True


def query_engram_context(task_description: str, limit: int = 3) -> list[dict[str, Any]]:
    """Auto-query Engram before executing a task for relevant past learnings."""
    try:
        results = engram.query_context(task_description, limit=limit)
        if results:
            log.info(f"Engram context: {len(results)} relevant memories found")
        return results
    except Exception as e:
        log.warning(f"Engram query failed: {e}")
        return []


def format_engram_context(results: list[dict[str, Any]]) -> str:
    """Format Engram query results into a context string for agents."""
    if not results:
        return ""
    lines = ["\n--- Relevant past learnings ---"]
    for r in results:
        lines.append(f"[{r.get('spec_id', '?')}] {r.get('summary', '')}")
    lines.append("---")
    return "\n".join(lines)


def scan_and_store_pipeline():
    """Scan process/completed/ for unregistered completions and store them."""
    import glob
    completed_dirs = glob.glob(os.path.join(PROCESS_DIR, "completed", "*"))
    stored = 0
    for d in sorted(completed_dirs):
        spec_file = os.path.join(d, "SPEC.md")
        leccion_file = os.path.join(d, "LECCION*.md")
        if not os.path.exists(spec_file):
            continue
        spec_name = os.path.basename(d)
        spec_id = spec_name.split("-", 1)[1] if "-" in spec_name else spec_name
        existing = engram.get_by_spec(spec_id)
        if existing:
            continue
        summary = f"Pipeline completed: {spec_name}"
        tags = ["pipeline", "spec"]
        leccion_matches = glob.glob(leccion_file)
        if leccion_matches:
            tags.append("leccion")
        store_spec_completion(spec_id, summary, tags)
        stored += 1
    return stored
