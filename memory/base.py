from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class MemoryResult:
    key: str
    data: dict | None = None
    found: bool = False
    error: str | None = None
    store_type: str = ""


class MemoryStore(ABC):
    name: str = ""

    @abstractmethod
    async def store(self, key: str, data: dict, ttl: int | None = None) -> MemoryResult:
        ...

    @abstractmethod
    async def retrieve(self, key: str) -> MemoryResult:
        ...

    @abstractmethod
    async def search(self, query: str | dict, top_k: int = 5) -> list[MemoryResult]:
        ...

    @abstractmethod
    async def delete(self, key: str) -> bool:
        ...

    @abstractmethod
    async def list_keys(self, prefix: str = "") -> list[str]:
        ...
