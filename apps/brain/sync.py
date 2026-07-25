"""Unified Brain v2 — Sincronización.

BrainSyncer orquesta los ingestores para poblar el cerebro unificado.
Cada ingestor es independiente — puede fallar sin romper el resto.
"""

import json
import logging
import os
import sqlite3
import time
from datetime import datetime
from typing import Optional

from apps.brain.models import SyncStatus

log = logging.getLogger("brain.sync")


class BrainSyncer:
    """Sincronizador de todas las fuentes de conocimiento al cerebro unificado."""

    def __init__(self, brain):
        self.brain = brain
        self.config = brain.config
        self.status = SyncStatus()

    def full_sync(self) -> SyncStatus:
        """Ejecuta sync completa de todos los ingestores."""
        log.info("🧠 BrainSync FULL starting...")
        self.status.ingestor_results = {}
        self.status.errors = []

        ingestors = [
            ("engram", self._sync_engram),
            ("events", self._sync_events),
            ("lecciones", self._sync_lecciones),
            ("truth", self._sync_truth),
        ]

        for name, ingestor in ingestors:
            try:
                t0 = time.time()
                result = ingestor()
                elapsed = time.time() - t0
                self.status.ingestor_results[name] = {
                    "status": "ok",
                    "count": result.get("count", 0),
                    "elapsed_s": round(elapsed, 2),
                }
                if "nodes" in result:
                    self.status.total_nodes += result["nodes"]
                log.info(f"  ✅ {name}: {result.get('count', 0)} items ({elapsed:.1f}s)")
            except Exception as e:
                self.status.ingestor_results[name] = {"status": "error", "error": str(e)}
                self.status.errors.append(f"{name}: {e}")
                log.warning(f"  ⚠️ {name}: {e}")

        log.info(f"🧠 BrainSync done — {self.status.total_nodes} total nodes")
        return self.status

    # ─── Ingestors ──────────────────────────────────────

    def _sync_engram(self) -> dict:
        """Ingesta memorias de Engram → Neo4j."""
        if not self.brain.engram:
            return {"count": 0, "status": "no_engram"}

        cur = self.brain.engram.execute(
            "SELECT key, value, layer, importance, created_at FROM memories ORDER BY created_at DESC"
        )
        count = 0
        for row in cur.fetchall():
            self._upsert_neo4j_node({
                "type": "MEMORY",
                "name": row["key"],
                "description": str(row["value"])[:500],
                "layer": row["layer"],
                "importance": row["importance"],
                "created_at": row["created_at"] or datetime.now().isoformat(),
            })
            count += 1

        return {"count": count, "nodes": count}

    def _sync_events(self) -> dict:
        """Ingesta eventos de events.jsonl → Neo4j."""
        if not os.path.exists(self.config.events_path):
            return {"count": 0, "status": "no_events_file"}

        count = 0
        with open(self.config.events_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                    self._upsert_neo4j_node({
                        "type": "EVENT",
                        "name": event.get("type", "unknown"),
                        "description": json.dumps(event.get("data", {}))[:300],
                        "producer": event.get("producer", ""),
                        "created_at": event.get("timestamp", ""),
                    })
                    count += 1
                except (json.JSONDecodeError, Exception):
                    continue

        return {"count": count, "nodes": count}

    def _sync_lecciones(self) -> dict:
        """Ingesta lecciones aprendidas → Neo4j."""
        count = 0
        for path in self.config.lecciones_paths:
            full_path = os.path.join(os.getcwd(), path) if not os.path.isabs(path) else path
            if not os.path.exists(full_path):
                continue
            try:
                content = open(full_path).read()
                self._upsert_neo4j_node({
                    "type": "LECCION",
                    "name": f"Lección: {os.path.basename(path)}",
                    "description": content[:500],
                    "source": path,
                    "created_at": datetime.now().isoformat(),
                })
                count += 1
            except Exception as e:
                log.warning(f"Lecciones ingestor {path}: {e}")

        return {"count": count, "nodes": count}

    def _sync_truth(self) -> dict:
        """Ingesta información de TRUTH.md → Neo4j."""
        truth_paths = [
            "constitution/TRUTH.md",
            os.path.expanduser("~/.hermes/memories/TRUTH.md"),
        ]
        count = 0
        for path in truth_paths:
            if not os.path.exists(path):
                continue
            try:
                content = open(path).read()
                # Crear nodo con secciones principales
                sections = self._parse_truth_sections(content)
                for section_name, section_content in sections.items():
                    self._upsert_neo4j_node({
                        "type": "TRUTH",
                        "name": f"TRUTH: {section_name}",
                        "description": section_content[:500],
                        "created_at": datetime.now().isoformat(),
                    })
                    count += 1
            except Exception as e:
                log.warning(f"Truth ingestor {path}: {e}")

        return {"count": count, "nodes": count}

    # ─── Helpers ────────────────────────────────────────

    def _upsert_neo4j_node(self, props: dict):
        """Crea un nodo en Neo4j si no existe (MERGE por name+type)."""
        if not self.brain.neo4j:
            return
        try:
            with self.brain.neo4j.session() as s:
                s.run(
                    """MERGE (n:Knowledge {name: $name, type: $type})
                       SET n += $props, n.updated_at = datetime()
                    """,
                    name=props.get("name", "unknown"),
                    type=props.get("type", "GENERIC"),
                    props={k: v for k, v in props.items() if k not in ("name", "type")},
                )
        except Exception as e:
            log.warning(f"Neo4j upsert error: {e}")

    def _parse_truth_sections(self, content: str) -> dict:
        """Parsea TRUTH.md en secciones por ## headers."""
        sections = {}
        current_section = "header"
        current_lines = []
        for line in content.split("\n"):
            if line.startswith("## "):
                if current_lines:
                    sections[current_section] = "\n".join(current_lines).strip()
                current_section = line.replace("## ", "").strip()
                current_lines = []
            else:
                current_lines.append(line)
        if current_lines:
            sections[current_section] = "\n".join(current_lines).strip()
        return sections

    def close(self):
        pass
