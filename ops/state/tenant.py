"""Tenant-aware MemoryStore wrapper (HAS-011)
Wraps any MemoryStore and prefixes keys with tenant_id for isolation.
"""
from memory.base import MemoryResult, MemoryStore


class TenantAwareStore(MemoryStore):
    """Wraps a MemoryStore with tenant_id key prefixing."""

    def __init__(self, store: MemoryStore, tenant_id: str = "default"):
        self._store = store
        self._tenant = tenant_id

    @property
    def name(self) -> str:
        return f"{self._store.name}:{self._tenant}"

    def _tenant_key(self, key: str) -> str:
        return f"{self._tenant}:{key}"

    def _strip_tenant(self, key: str) -> str:
        prefix = f"{self._tenant}:"
        if key.startswith(prefix):
            return key[len(prefix):]
        return key

    async def store(self, key: str, data: dict, ttl: int | None = None) -> MemoryResult:
        result = await self._store.store(self._tenant_key(key), data, ttl)
        result.key = self._strip_tenant(result.key)
        return result

    async def retrieve(self, key: str) -> MemoryResult:
        result = await self._store.retrieve(self._tenant_key(key))
        result.key = self._strip_tenant(result.key)
        return result

    async def search(self, query: str | dict, top_k: int = 5) -> list[MemoryResult]:
        results = await self._store.search(query, top_k)
        tenant_prefix = f"{self._tenant}:"
        filtered = []
        for r in results:
            if r.key.startswith(tenant_prefix):
                r.key = self._strip_tenant(r.key)
                filtered.append(r)
            elif self._tenant == "default":
                r.key = self._strip_tenant(r.key)
                filtered.append(r)
        return filtered[:top_k]

    async def delete(self, key: str) -> bool:
        return await self._store.delete(self._tenant_key(key))

    async def list_keys(self, prefix: str = "") -> list[str]:
        keys = await self._store.list_keys(f"{self._tenant}:{prefix}")
        return [self._strip_tenant(k) for k in keys]
