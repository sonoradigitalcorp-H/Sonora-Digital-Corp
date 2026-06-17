"""Mock Qdrant client for testing."""


class MockQdrantClient:
    def __init__(self, available=True):
        self.available = available
        self.collections = {}
        self.points = {}

    def get_collections(self):
        if not self.available:
            raise Exception("Qdrant not available")
        from types import SimpleNamespace
        return SimpleNamespace(collections=list(self.collections.keys()))

    def recreate_collection(self, collection_name, vectors_config=None):
        self.collections[collection_name] = []
        return True

    def upsert(self, collection_name, points=None):
        if collection_name not in self.collections:
            self.collections[collection_name] = []
        for p in points or []:
            self.collections[collection_name].append(p)
        return True

    def search(self, collection_name, query_vector=None, limit=10):
        results = []
        for p in self.collections.get(collection_name, []):
            from types import SimpleNamespace
            results.append(SimpleNamespace(
                id=p.id,
                score=0.95,
                payload=p.payload or {},
                version=0
            ))
        return results[:limit]

    def close(self):
        pass
