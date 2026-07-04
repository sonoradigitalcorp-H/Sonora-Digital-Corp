from apps.brain.models import KnowledgeNode, KnowledgeType
from datetime import datetime

LABEL_MAP = {
    "Service": KnowledgeType.SERVICE,
    "Spec": KnowledgeType.SPEC,
    "Person": KnowledgeType.PERSON,
    "Capability": KnowledgeType.CAPABILITY,
    "Achievement": KnowledgeType.ACHIEVEMENT,
    "Session": KnowledgeType.SESSION,
}

class Neo4jIngestor:
    def ingest(self, brain) -> int:
        with brain.neo4j.session() as s:
            result = s.run(
                "MATCH (n) "
                "OPTIONAL MATCH (n)-[r]->(m) "
                "RETURN n, labels(n) as labels, keys(n) as keys, "
                "collect({rel: type(r), target: id(m)}) as rels"
            )
            count = 0
            for record in result:
                node_data = record["n"]
                labels = record["labels"]
                ktype = LABEL_MAP.get(labels[0], KnowledgeType.MEMORY) if labels else KnowledgeType.MEMORY
                node = KnowledgeNode(
                    id=f"neo4j-{node_data.element_id}",
                    type=ktype,
                    label=str(node_data.get("name", node_data.get("title", ""))),
                    summary=str(node_data.get("description", node_data.get("summary", ""))),
                    details=dict(node_data),
                    source="neo4j",
                    created_at=datetime.utcnow()
                )
                self._index_to_qdrant(brain, node)
                count += 1
        return count

    def _index_to_qdrant(self, brain, node: KnowledgeNode):
        from qdrant_client.http import models
        from qdrant_client.models import PointStruct
        import uuid

        collections = brain.qdrant.get_collections().collections
        if "brain-knowledge" not in [c.name for c in collections]:
            brain.qdrant.create_collection(
                collection_name="brain-knowledge",
                vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE)
            )

        brain.qdrant.upsert(
            collection_name="brain-knowledge",
            points=[PointStruct(
                id=str(uuid.uuid5(uuid.NAMESPACE_DNS, node.id)),
                vector=[0.0] * 384,
                payload={
                    "id": node.id,
                    "type": node.type.value,
                    "label": node.label,
                    "summary": node.summary,
                    "source": node.source,
                }
            )]
        )
