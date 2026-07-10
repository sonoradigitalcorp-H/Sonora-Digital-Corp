#!/usr/bin/env python3
"""Knowledge Ingestion Pipeline — Cada sesión completada → knowledge graph.

Lee SESSION.md, LECCION.md, events.jsonl, SPEC.md de cada sesión en
process/completed/ y los ingesta al brain (Neo4j + Qdrant + engram).

Uso: python3 scripts/ingest-session-knowledge.py [--session SPEC-xxx] [--all]
"""

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

REPO = Path(__file__).resolve().parent.parent
COMPLETED_DIR = REPO / "process" / "completed"
STATE_EVENTS = REPO / "state" / "events" / "events.jsonl"


def extract_session_metadata(session_dir: Path) -> dict:
    meta = {"session_id": session_dir.name, "path": str(session_dir)}

    session_file = session_dir / "SESSION.md"
    if session_file.exists():
        text = session_file.read_text()
        for line in text.splitlines():
            if line.startswith("# "):
                meta["title"] = line.replace("# ", "").strip()
            if line.startswith("## ") and "Resumen" not in line:
                meta.setdefault("sections", []).append(line.replace("## ", "").strip())

    spec_file = session_dir / "SPEC.md"
    if spec_file.exists():
        text = spec_file.read_text()
        for line in text.splitlines():
            if line.startswith("## Objetivo") or line.startswith("## Objective"):
                meta["objective"] = line.split(":", 1)[-1].strip() if ":" in line else ""

    leccion_file = session_dir / "LECCION.md"
    if leccion_file.exists():
        meta["has_lecciones"] = True
        text = leccion_file.read_text()
        import re
        lessons = re.findall(r"\d+\.\s*(.*?)(?=\n\d+\.|\n\n|\Z)", text, re.DOTALL)
        meta["lessons"] = [l.strip() for l in lessons if l.strip()]

    events_file = session_dir / "events.jsonl"
    if events_file.exists():
        with open(events_file) as f:
            meta["events"] = sum(1 for _ in f)

    return meta


def ingest_to_engram(metadata: dict) -> bool:
    try:
        from apps.brain.ingestors.engram_ingestor import ingest
        ingest({
            "type": "session_completed",
            "session_id": metadata["session_id"],
            "title": metadata.get("title", metadata["session_id"]),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata,
        })
        logger.info("Ingested to engram: %s", metadata["session_id"])
        return True
    except ImportError:
        logger.warning("engram_ingestor not available, writing to events.jsonl instead")
        STATE_EVENTS.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "event": "knowledge.session_ingested",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": metadata,
        }
        with open(STATE_EVENTS, "a") as f:
            f.write(json.dumps(entry) + "\n")
        return True
    except Exception as e:
        logger.error("Failed to ingest %s: %s", metadata["session_id"], e)
        return False


def ingest_session(session_id: str) -> dict:
    session_dir = COMPLETED_DIR / session_id
    if not session_dir.exists():
        return {"status": "not_found", "session": session_id}

    meta = extract_session_metadata(session_dir)
    ok = ingest_to_engram(meta)
    return {"status": "ingested" if ok else "failed", "session": session_id, "metadata": meta}


def ingest_all() -> list[dict]:
    results = []
    for session_dir in sorted(COMPLETED_DIR.iterdir()):
        if not session_dir.is_dir():
            continue
        result = ingest_session(session_dir.name)
        results.append(result)
    return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Ingest session knowledge to brain")
    parser.add_argument("--session", help="Specific session ID (e.g. SPEC-20260710)")
    parser.add_argument("--all", action="store_true", help="Ingest all sessions")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    if args.session:
        results = [ingest_session(args.session)]
    elif args.all:
        results = ingest_all()
    else:
        logger.error("Specify --session or --all")
        sys.exit(1)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        ingested = sum(1 for r in results if r["status"] == "ingested")
        failed = sum(1 for r in results if r["status"] == "failed")
        print(f"Ingested: {ingested} | Failed: {failed} | Total: {len(results)}")


if __name__ == "__main__":
    main()
