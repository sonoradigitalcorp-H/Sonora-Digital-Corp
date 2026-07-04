import json
from pathlib import Path
from apps.brain.models import KnowledgeNode, KnowledgeType
from datetime import datetime

class EventsIngestor:
    def ingest(self, brain) -> int:
        path = Path(brain.config.events_path)
        if not path.exists():
            return 0

        count = 0
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue

                event_id = event.get("event", "unknown")
                ts = event.get("timestamp", datetime.utcnow().isoformat())
                producer = event.get("producer", "unknown")
                payload = event.get("payload", {})

                node = KnowledgeNode(
                    id=f"event-{event_id}-{ts}",
                    type=KnowledgeType.EVENT,
                    label=event_id,
                    summary=str(payload.get("detail", "")),
                    details={"producer": producer, "payload": payload},
                    source="events",
                    created_at=datetime.utcnow()
                )

                with brain.neo4j.session() as s:
                    s.run(
                        "MERGE (n:Knowledge {id: $id}) "
                        "SET n.type = $type, n.label = $label, n.summary = $summary, "
                        "n.source = $source, n.updated_at = $updated_at",
                        id=node.id, type=node.type.value, label=node.label,
                        summary=node.summary, source=node.source,
                        updated_at=datetime.utcnow().isoformat()
                    )
                count += 1
        return count
