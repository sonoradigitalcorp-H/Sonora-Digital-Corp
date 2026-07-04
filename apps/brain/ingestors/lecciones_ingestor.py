import json
from pathlib import Path
from apps.brain.models import KnowledgeNode, KnowledgeType
from datetime import datetime

class LeccionesIngestor:
    def ingest(self, brain) -> int:
        paths = [
            Path("products/yami/memory/lecciones.json"),
            Path("sonora-enterprise-os/memory/lecciones.json"),
        ]
        count = 0
        for path in paths:
            if not path.exists():
                continue
            try:
                with open(path) as f:
                    data = json.load(f)
            except (json.JSONDecodeError, Exception):
                continue

            lecciones = data if isinstance(data, list) else [data]
            for lec in lecciones:
                node = KnowledgeNode(
                    id=f"leccion-{lec.get('id', hash(str(lec)))}",
                    type=KnowledgeType.LECCION,
                    label=lec.get("titulo", lec.get("title", "Lección")),
                    summary=lec.get("resumen", lec.get("summary", "")),
                    details=lec,
                    source="lecciones",
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
        return count
