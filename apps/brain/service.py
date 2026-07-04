import sqlite3
from pathlib import Path
from apps.brain.config import BrainConfig

class BrainService:
    def __init__(self, config: BrainConfig = None):
        self.config = config or BrainConfig()
        self.neo4j = None
        self.qdrant = None
        self._connect()

    def _connect(self):
        from neo4j import GraphDatabase
        from qdrant_client import QdrantClient
        self.neo4j = GraphDatabase.driver(
            self.config.neo4j_uri,
            auth=(self.config.neo4j_user, self.config.neo4j_password)
        )
        self.qdrant = QdrantClient(
            host=self.config.qdrant_host,
            port=self.config.qdrant_port
        )

    def ready(self) -> dict:
        status = {"neo4j": False, "qdrant": False, "engram": False}
        try:
            with self.neo4j.session() as s:
                s.run("RETURN 1").single()
            status["neo4j"] = True
        except Exception as e:
            status["neo4j_error"] = str(e)

        try:
            self.qdrant.get_collections()
            status["qdrant"] = True
        except Exception as e:
            status["qdrant_error"] = str(e)

        try:
            conn = sqlite3.connect(self.config.engram_path)
            conn.execute("SELECT 1")
            conn.close()
            status["engram"] = True
        except Exception as e:
            status["engram_error"] = str(e)

        return status

    def close(self):
        if self.neo4j:
            self.neo4j.close()
