import sqlite3
from apps.brain.models import KnowledgeNode, KnowledgeType
from datetime import datetime

class EngramIngestor:
    def ingest(self, brain) -> int:
        path = brain.config.engram_path
        if not path or not __import__('pathlib').Path(path).exists():
            return 0
        conn = sqlite3.connect(path)
        tables = [t[0] for t in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        if "memories" not in tables:
            conn.close()
            return 0
        cur = conn.execute("SELECT id, spec_id, tag, summary, context, importance, layer, timestamp FROM memories")
        count = 0
        for row in cur:
            node = KnowledgeNode(
                id=f"engram-{row[0]}",
                type=KnowledgeType.MEMORY,
                label=str(row[1] or ""),
                summary=str(row[3] or ""),
                details={"context": str(row[4] or ""), "layer": str(row[6] or "")},
                tags=str(row[2] or "").split(",") if row[2] else [],
                importance=int(row[5] or 1),
                source="engram",
                created_at=datetime.utcnow()
            )
            self._index_node(brain, node)
            count += 1
        conn.close()
        return count

    def _index_node(self, brain, node: KnowledgeNode):
        with brain.neo4j.session() as s:
            s.run(
                "MERGE (n:Knowledge {id: $id}) "
                "SET n.type = $type, n.label = $label, n.summary = $summary, "
                "n.importance = $importance, n.source = $source, n.updated_at = $updated_at",
                id=node.id, type=node.type.value, label=node.label,
                summary=node.summary, importance=node.importance,
                source=node.source, updated_at=datetime.utcnow().isoformat()
            )
