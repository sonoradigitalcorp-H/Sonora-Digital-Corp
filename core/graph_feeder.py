"""GraphFeeder — alimenta Neo4j desde events, engram y specs automaticamente."""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from src.core.neo4j_store import (
    _post,
    create_relationship,
    get_stats,
    query,
    upsert_node,
)

log = logging.getLogger(__name__)
REPO = Path(__file__).resolve().parent.parent.parent


class GraphFeeder:
    """Conecta Event Bus + Engram + Specs -> Neo4j."""

    def __init__(self, neo4j_available: Optional[bool] = None):
        from src.core.neo4j_store import test_connection
        self._available = neo4j_available if neo4j_available is not None else test_connection()

    def feed_from_events(self, events_file: str = "state/logs/events.jsonl") -> int:
        if not self._available:
            return 0
        path = Path(events_file) if os.path.isabs(events_file) else REPO / events_file
        if not path.exists():
            log.warning("Events file not found: %s", path)
            return 0
        count = 0
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    evt = json.loads(line)
                except json.JSONDecodeError:
                    continue
                event_type = evt.get("event", evt.get("type", ""))
                ts = evt.get("timestamp", datetime.now(timezone.utc).isoformat())
                upsert_node("Event", {"id": f"event:{event_type}:{ts}"},
                            {"type": event_type, "payload": json.dumps(evt.get("payload", {})),
                             "producer": evt.get("producer", "unknown"), "timestamp": ts})
                count += 1
        log.info("GraphFeeder: %d events processed", count)
        return count

    def feed_from_engram(self, engram_instance, layers: list = None) -> int:
        if not self._available:
            return 0
        layers = layers or [3, 4, 5, 6]
        synced = 0
        for layer in layers:
            memories = engram_instance.query_context("", limit=200)
            for mem in memories:
                if mem.get("layer") != layer and isinstance(layer, int):
                    pass
                if mem.get("layer") not in layers:
                    continue
                spec_id = mem.get("spec_id", f"mem:{mem.get('id', 'unknown')}")
                upsert_node("Knowledge", {"id": spec_id},
                            {"summary": mem.get("summary", "")[:500],
                             "tag": mem.get("tag", ""), "layer": mem.get("layer", 2),
                             "importance": mem.get("importance", 1),
                             "created": mem.get("created_at", ts_now()),
                             "source": "engram"})
                synced += 1
        log.info("GraphFeeder: %d engram memories synced", synced)
        return synced

    def feed_from_specs(self, specs_dir: str = "process") -> int:
        if not self._available:
            return 0
        base = REPO / specs_dir
        count = 0
        for pattern in ("**/SPEC-*.md", "**/ADR-*.md", "**/LECCION-*.md"):
            for path in sorted(base.glob(pattern)):
                node_type = {"SPEC": "Spec", "ADR": "ADR", "LECCION": "Leccion"}.get(path.stem.split("-")[0], "Doc")
                upsert_node(node_type, {"id": path.stem},
                            {"path": str(path.relative_to(REPO)), "title": path.stem,
                             "updated": ts_now()})
                count += 1
        return count

    def build_knowledge_graph(self, engram_instance) -> dict:
        if not self._available:
            return {"events": 0, "engram": 0, "specs": 0, "status": "neo4j_unavailable"}
        n_events = self.feed_from_events()
        n_engram = self.feed_from_engram(engram_instance)
        n_specs = self.feed_from_specs()
        stats = get_stats()
        return {"events": n_events, "engram": n_engram, "specs": n_specs,
                "nodes": stats.get("nodes", 0), "relationships": stats.get("relationships", 0),
                "status": "ok"}

    def cleanup_duplicates(self) -> int:
        if not self._available:
            return 0
        removed = 0
        for label in ("Contact", "Knowledge", "Session"):
            dups = query(
                f"MATCH (n:{label}) WITH n.id as id, collect(n) as nodes WHERE size(nodes) > 1 "
                f"UNWIND nodes[1..] as dup DETACH DELETE dup RETURN count(dup) as removed"
            )
            if dups and dups[0].get("removed", 0) > 0:
                removed += dups[0]["removed"]
        return removed


def ts_now() -> str:
    return datetime.now(timezone.utc).isoformat()
