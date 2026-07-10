import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

MEMORY_DIRS = [
    Path("state/memory/working"),
    Path("state/memory/project"),
    Path("state/memory/organization"),
]
DOCS_DIR = Path("docs")
COMPLETED_DIR = Path("process/completed")


def search_all_sources(query: str) -> list[dict]:
    results = []
    for mem_dir in MEMORY_DIRS:
        if not mem_dir.exists():
            continue
        for f in mem_dir.iterdir():
            if f.is_file() and query.lower() in f.read_text().lower():
                results.append({"source": str(mem_dir), "file": f.name})
    return results


def recent_sessions(limit: int = 5) -> list[dict]:
    if not COMPLETED_DIR.exists():
        return []
    sessions = sorted(COMPLETED_DIR.iterdir(), key=lambda p: p.name, reverse=True)
    return [{"session": s.name, "path": str(s)} for s in sessions[:limit]]


def synthesize(context: dict, user_query: str) -> dict:
    sources = search_all_sources(user_query)
    sessions = recent_sessions()
    return {
        "query": user_query,
        "sources_found": len(sources),
        "recent_sessions": sessions,
        "summary": f"Found {len(sources)} relevant sources across {len(MEMORY_DIRS)} memory stores.",
    }
