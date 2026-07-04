import sqlite3
from pathlib import Path
from apps.brain.models import KnowledgeNode, KnowledgeType
from datetime import datetime

class HermesIngestor:
    def ingest(self, brain) -> int:
        path = Path(brain.config.hermes_state_path)
        if not path.exists():
            return 0

        conn = sqlite3.connect(str(path))
        count = 0

        try:
            tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            table_names = [t[0] for t in tables]

            if "sessions" in table_names:
                cur = conn.execute("SELECT id, title, started_at, ended_at FROM sessions ORDER BY started_at DESC LIMIT 100")
                for row in cur:
                    node = KnowledgeNode(
                        id=f"hermes-session-{row[0]}",
                        type=KnowledgeType.SESSION,
                        label=str(row[1] or "Sin título"),
                        summary=f"Sesión Hermes del {row[2] or 'desconocido'}",
                        details={"session_id": row[0], "created": row[2], "updated": row[3]},
                        source="hermes",
                        created_at=datetime.utcnow()
                    )
                    with brain.neo4j.session() as s:
                        s.run(
                            "MERGE (n:Knowledge {id: $id}) SET n.type = $type, n.label = $label, "
                            "n.summary = $summary, n.source = $source, n.updated_at = $updated_at",
                            id=node.id, type=node.type.value, label=node.label,
                            summary=node.summary, source=node.source,
                            updated_at=datetime.utcnow().isoformat()
                        )
                    count += 1
        finally:
            conn.close()
        return count
