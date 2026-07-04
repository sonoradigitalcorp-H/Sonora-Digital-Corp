from apps.brain.service import BrainService
from apps.brain.ingestors.engram_ingestor import EngramIngestor
from apps.brain.ingestors.neo4j_ingestor import Neo4jIngestor
from apps.brain.ingestors.events_ingestor import EventsIngestor
from apps.brain.ingestors.hermes_ingestor import HermesIngestor
from apps.brain.ingestors.lecciones_ingestor import LeccionesIngestor
from apps.brain.ingestors.truth_ingestor import TruthIngestor
from datetime import datetime

class BrainSyncer:
    def __init__(self, brain: BrainService = None):
        self.brain = brain or BrainService()
        self.ingestors = [
            ("engram", EngramIngestor()),
            ("neo4j", Neo4jIngestor()),
            ("events", EventsIngestor()),
            ("hermes", HermesIngestor()),
            ("lecciones", LeccionesIngestor()),
            ("truth", TruthIngestor()),
        ]

    def full_sync(self) -> dict:
        results = {}
        for name, ingestor in self.ingestors:
            try:
                count = ingestor.ingest(self.brain)
                results[name] = {"status": "ok", "count": count}
            except Exception as e:
                results[name] = {"status": "error", "error": str(e)}
        results["timestamp"] = datetime.utcnow().isoformat()
        with self.brain.neo4j.session() as s:
            r = s.run("MATCH (n:Knowledge) RETURN count(n) as c").single()
            results["total_nodes"] = r["c"]
        return results

    def close(self):
        self.brain.close()
