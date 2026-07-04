import re
from pathlib import Path
from apps.brain.models import KnowledgeNode, KnowledgeType, KnowledgeRelation
from datetime import datetime

class TruthIngestor:
    def ingest(self, brain) -> int:
        path = Path("/home/ubuntu/.hermes/memories/TRUTH.md")
        if not path.exists():
            return 0

        content = path.read_text()
        count = 0

        # Parse services table: | port | Service | Type | Notes |
        service_pattern = re.findall(
            r'\|\s*(\d+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]*)',
            content
        )

        for port, service, stype, notes in service_pattern:
            port = port.strip()
            service = service.strip()
            if not port.isdigit():
                continue

            node = KnowledgeNode(
                id=f"service-{port}",
                type=KnowledgeType.SERVICE,
                label=service,
                summary=f"{service} en puerto {port} ({stype.strip()})",
                details={"port": port, "type": stype.strip(), "notes": notes.strip()},
                source="truth",
                created_at=datetime.utcnow()
            )
            with brain.neo4j.session() as s:
                s.run(
                    "MERGE (n:Knowledge {id: $id}) SET n.type = $type, n.label = $label, "
                    "n.summary = $summary, n.details = $details, n.source = $source, "
                    "n.updated_at = $updated_at",
                    id=node.id, type=node.type.value, label=node.label,
                    summary=node.summary, details=str(node.details),
                    source=node.source, updated_at=datetime.utcnow().isoformat()
                )
            count += 1

        # Parse people table
        people_pattern = re.findall(
            r'\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]*)',
            content
        )
        for person_row in people_pattern:
            name = person_row[0].strip()
            role = person_row[1].strip() if len(person_row) > 1 else ""
            if not name or name.startswith("Persona") or name.startswith("---"):
                continue

            node = KnowledgeNode(
                id=f"person-{name.lower().replace(' ', '-')}",
                type=KnowledgeType.PERSON,
                label=name,
                summary=f"{name} — {role}",
                details={"role": role, "notes": person_row[2].strip() if len(person_row) > 2 else ""},
                source="truth",
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
