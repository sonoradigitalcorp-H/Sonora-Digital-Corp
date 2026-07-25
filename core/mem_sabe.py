"""MemSabe — Conscious memory layer over Engram with semantic reasoning, graph sync, and cross-channel context."""

import json
import logging
from typing import Any, Optional

from src.core.engram import Engram

try:
    import requests
except ImportError:
    requests = None

log = logging.getLogger(__name__)

LAYER_NAMES = ["working", "task", "project", "customer", "business", "historical", "strategic"]


class MemSabe:
    """Memoria que sabe — high-level reasoning layer over the Engram memory system.

    Provides cross-session context unification, Neo4j graph sync, proactive knowledge
    suggestion, pattern detection, and ADR compliance verification.
    """

    def __init__(
        self,
        engram_instance: Engram,
        neo4j_uri: str = "",
        qdrant_host: str = "",
    ):
        self._engram = engram_instance
        self._neo4j_uri = neo4j_uri
        self._qdrant_host = qdrant_host

    def sabe(self, query: str, context: Optional[dict] = None) -> dict:
        """Saber — intelligent consult combining engram retrieval with relationship analysis.

        :param query: Search query string
        :param context: Optional dict with additional filtering context
        :return: Dict with found, memories, and insight fields
        """
        memories = self._engram.query_context(query, limit=15)
        if not memories:
            return {"found": False, "memories": [], "insight": ""}
        analysis = self._analyze(memories, context or {})
        return {"found": True, "memories": memories, "insight": analysis}

    def guarda(
        self,
        key: str,
        value: Any,
        layer: int = 2,
        importance: str = "medium",
        channels: Optional[list[str]] = None,
    ) -> str:
        """Guardar — store a value with channel metadata for multi-channel traceability.

        :param key: Memory key (used as spec_id)
        :param value: Value to store
        :param layer: Memory layer (0-6, default 2=project)
        :param importance: Importance level string
        :param channels: List of source channels (e.g. ["telegram", "web"])
        :return: Memory ID as string
        """
        mem_id = self._engram.store_learning(
            spec_id=key,
            tag=",".join(channels or []),
            summary=str(value)[:500],
            context=json.dumps({"channels": channels or [], "key": key}),
            importance=importance,
            layer=LAYER_NAMES[layer] if 0 <= layer < len(LAYER_NAMES) else "project",
        )
        return str(mem_id)

    def sync_knowledge_graph(self) -> int:
        """Sync layers 3-6 from Engram to Neo4j as nodes and relationships.

        :return: Number of memories synced
        """
        if not self._neo4j_uri or not requests:
            log.warning("Neo4j not configured or requests library not available")
            return 0
        synced = 0
        for layer_id in (3, 4, 5, 6):
            memories = self._engram.query_context("", limit=100)
            for mem in memories:
                if mem.get("layer") == layer_id:
                    try:
                        resp = requests.post(
                            f"{self._neo4j_uri}/api/knowledge/memory",
                            json={
                                "spec_id": mem.get("spec_id"),
                                "summary": mem.get("summary"),
                                "layer": layer_id,
                            },
                            timeout=5,
                        )
                        if resp.ok:
                            synced += 1
                    except requests.RequestException:
                        pass
        return synced

    def get_channel_context(self, user_id: str, channel: str) -> dict:
        """Get context specific to a channel for a user.

        :param user_id: User identifier
        :param channel: Channel name (telegram, whatsapp, web, voice)
        :return: Dict with channel memories
        """
        results = self._engram.query_context(f"{user_id} {channel}", limit=20)
        return {"channel": channel, "user_id": user_id, "memories": results, "count": len(results)}

    def get_unified_context(self, user_id: str) -> dict:
        """Get unified context across ALL channels for a user.

        :param user_id: User identifier
        :return: Dict with aggregated cross-channel context
        """
        results = self._engram.query_context(user_id, limit=50)
        channels: set[str] = set()
        for r in results:
            if r.get("tag"):
                for c in r["tag"].split(","):
                    ch = c.strip()
                    if ch:
                        channels.add(ch)
        return {
            "user_id": user_id,
            "channels": sorted(channels),
            "memory_count": len(results),
            "recent_memories": results[:20],
        }

    def verify_adr_compliance(self, adr_id: str) -> dict:
        """Verify whether an Architectural Decision Record is being followed.

        :param adr_id: ADR identifier
        :return: Dict with compliance status and evidence
        """
        memories = self._engram.get_by_spec(adr_id)
        if not memories:
            return {
                "adr_id": adr_id,
                "compliant": False,
                "reason": "No memories found for this ADR",
            }
        keywords = ["implemented", "compliant", "applied", "enforced"]
        evidence = [
            m.get("summary", "")
            for m in memories
            if any(k in m.get("summary", "").lower() for k in keywords)
        ]
        return {
            "adr_id": adr_id,
            "compliant": len(evidence) > 0,
            "memories": len(memories),
            "evidence": evidence,
        }

    def suggest_relevant_knowledge(self, task_context: str) -> list[dict]:
        """Suggest relevant past knowledge for a task context.

        :param task_context: Description of the current task
        :return: List of relevant memory dicts
        """
        return self._engram.query_context(task_context, limit=10)

    def build_continuity_summary(self, user_id: str, channels: list[str]) -> dict:
        """Build a cross-channel continuity summary for a user.

        :param user_id: User identifier
        :param channels: List of channels to aggregate
        :return: Dict with unified continuity context
        """
        all_memories: list[dict] = []
        for ch in channels:
            ctx = self.get_channel_context(user_id, ch)
            all_memories.extend(ctx.get("memories", []))
        return {
            "user_id": user_id,
            "channels": channels,
            "total_memories": len(all_memories),
            "continuity": all_memories[:10],
        }

    def detect_patterns(self, layer: int) -> list[dict[str, Any]]:
        """Detect recurring patterns in memories at a given layer.

        :param layer: Layer number to analyze (0-6)
        :return: List of pattern dicts with tag, count, and samples
        """
        results = self._engram.query_context("", limit=200)
        layer_mems = [m for m in results if m.get("layer") == layer]
        tag_groups: dict[str, list[dict]] = {}
        for m in layer_mems:
            tag = m.get("tag", "unknown")
            tag_groups.setdefault(tag, []).append(m)
        patterns = []
        for tag, mems in tag_groups.items():
            if len(mems) >= 2:
                patterns.append({
                    "tag": tag,
                    "count": len(mems),
                    "samples": [m.get("summary", "") for m in mems[:3]],
                })
        return patterns

    def _analyze(self, memories: list[dict], context: dict) -> str:
        specs: set[str] = set()
        tags: set[str] = set()
        for m in memories:
            if m.get("spec_id"):
                specs.add(m["spec_id"])
            if m.get("tag"):
                for t in m["tag"].split(","):
                    t = t.strip()
                    if t:
                        tags.add(t)
        parts = []
        if specs:
            sorted_specs = sorted(specs)[:5]
            parts.append(f"Related to {len(specs)} specifications: {', '.join(sorted_specs)}")
        if tags:
            sorted_tags = sorted(tags)[:5]
            parts.append(f"Tags: {', '.join(sorted_tags)}")
        return "; ".join(parts) if parts else "No direct relationships found"
