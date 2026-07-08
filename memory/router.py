from memory.base import MemoryResult, MemoryStore
from memory.types import MemoryRef


class MemoryRouter:
    def __init__(self):
        self.stores: dict[str, MemoryStore] = {}

    def register(self, memory_type: str, store: MemoryStore):
        self.stores[memory_type] = store

    def get_store(self, memory_type: str) -> MemoryStore | None:
        return self.stores.get(memory_type)

    async def store(self, ref: MemoryRef, data: dict) -> MemoryResult:
        store = self.stores.get(ref.type)
        if not store:
            return MemoryResult(key=ref.key, found=False, error=f"Unknown memory type: {ref.type}", store_type=ref.type)
        return await store.store(ref.key, data, ref.ttl)

    async def retrieve(self, ref: MemoryRef) -> MemoryResult:
        store = self.stores.get(ref.type)
        if not store:
            return MemoryResult(key=ref.key, found=False, error=f"Unknown memory type: {ref.type}", store_type=ref.type)
        return await store.retrieve(ref.key)

    async def search(self, ref_type: str, query: str | dict, top_k: int = 5) -> list[MemoryResult]:
        store = self.stores.get(ref_type)
        if not store:
            return []
        return await store.search(query, top_k)

    async def search_all(self, query: str, top_k: int = 3) -> dict[str, list[MemoryResult]]:
        results = {}
        for mtype, store in self.stores.items():
            results[mtype] = await store.search(query, top_k)
        return results

    async def delete(self, ref: MemoryRef) -> bool:
        store = self.stores.get(ref.type)
        if not store:
            return False
        return await store.delete(ref.key)

    def list_types(self) -> list[str]:
        return list(self.stores.keys())
