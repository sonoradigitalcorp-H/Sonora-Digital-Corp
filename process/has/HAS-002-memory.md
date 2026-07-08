# HAS-002 — Hermes Architecture Standard: Memory Contracts

**Status:** Draft v1
**Domain:** memory
**Updated:** 2026-07-08
**Depends on:** HAS-000, HAS-001

---

## 1. Purpose

Define a uniform `MemoryStore` interface for all memory types. The system does not have "one RAG" — it has typed memory stores, each with the same contract, used for different purposes.

---

## 2. Memory Types

| Type | Store | TTL | Purpose | Current impl |
|---|---|---|---|---|
| **Working** | Redis | Session | Current conversation context | Redis streams |
| **Semantic** | Qdrant | Indefinite | Embeddings + similarity search | Qdrant |
| **Long** | PostgreSQL | Indefinite | Events, lessons, history | Engram.db / SQLite |
| **Knowledge Graph** | Neo4j | Indefinite | Entity relationships | Neo4j |
| **Business** | PostgreSQL | Indefinite | Structured business data | PostgreSQL |
| **Event** | Redis Streams | 7 days | Event log for processing | Redis streams |
| **File** | S3 / local | Indefinite | Documents, images, videos | Local filesystem |

---

## 3. MemoryStore Interface

Every memory type implements this contract. Agents never know which store they're talking to — they call `MemoryStore`:

```python
from abc import ABC, abstractmethod
from typing import Any

class MemoryStore(ABC):
    @abstractmethod
    async def store(self, key: str, data: dict, ttl: int | None = None) -> str:
        """Store data. Returns the key/ID."""

    @abstractmethod
    async def retrieve(self, key: str) -> dict | None:
        """Retrieve data by key."""

    @abstractmethod
    async def search(self, query: str | dict, top_k: int = 5) -> list[dict]:
        """Semantic or structured search."""

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete by key."""

    @abstractmethod
    async def list_keys(self, prefix: str = "") -> list[str]:
        """List keys with optional prefix."""
```

### Type hint: how agents specify memory type

```python
@dataclass
class MemoryRef:
    type: Literal["working", "semantic", "long", "graph", "business", "event", "file"]
    key: str
    ttl: int | None = None
```

---

## 4. Current Implementation → HAS Contract

| Current | HAS contract | Migration |
|---|---|---|
| `engram.db` (SQLite) | `LongMemory(MemoryStore)` | Wrap existing DB in MemoryStore |
| `QdrantClient` (direct) | `SemanticMemory(MemoryStore)` | Wrap in MemoryStore |
| `Neo4jDriver` (direct) | `GraphMemory(MemoryStore)` | Wrap in MemoryStore |
| `Redis` streams | `WorkingMemory(MemoryStore)` + `EventMemory(MemoryStore)` | Split concerns |
| `PostgreSQL` | `BusinessMemory(MemoryStore)` | Wrap in MemoryStore |

### Migration: `apps/jarvis/src/core/memory/`

```python
# Before
from qdrant_client import QdrantClient
qdrant = QdrantClient(...)
qdrant.search(...)

# After
from memory import SemanticMemory
memory = SemanticMemory(config)
await memory.search(...)
```

---

## 5. Memory Router

A lightweight router sits between agents and stores. Agents call `memory.retrieve()` and the router decides which store(s) to query based on the `MemoryRef.type`:

```python
class MemoryRouter:
    def __init__(self):
        self.stores: dict[str, MemoryStore] = {}

    def register(self, memory_type: str, store: MemoryStore):
        self.stores[memory_type] = store

    async def retrieve(self, ref: MemoryRef) -> dict | None:
        store = self.stores.get(ref.type)
        if not store:
            raise ValueError(f"Unknown memory type: {ref.type}")
        return await store.retrieve(ref.key)

    async def search_all(self, query: str, top_k: int = 3) -> dict[str, list[dict]]:
        """Search ALL memory stores — returns results grouped by type."""
        results = {}
        for mtype, store in self.stores.items():
            results[mtype] = await store.search(query, top_k)
        return results
```

---

## 6. Directory Structure

```
memory/
├── __init__.py
├── router.py              # MemoryRouter
├── base.py                # MemoryStore ABC
├── types.py               # MemoryRef, Literal types
├── stores/
│   ├── __init__.py
│   ├── working.py          # Redis-backed
│   ├── semantic.py         # Qdrant-backed
│   ├── long.py             # SQLite/PostgreSQL-backed
│   ├── graph.py            # Neo4j-backed
│   ├── business.py         # PostgreSQL-backed
│   ├── event.py            # Redis Streams-backed
│   └── file.py             # S3/local-backed
├── migrations/
│   ├── 001-engram-to-long.py
│   └── 002-qdrant-to-semantic.py
└── tests/
    ├── test_router.py
    ├── test_stores.py
    └── test_integration.py
```

---

## 7. Events

The Memory System publishes these events:

| Event | When | Payload |
|---|---|---|
| `memory.stored` | Data stored | `{ type, key, size }` |
| `memory.retrieved` | Data retrieved | `{ type, key, found }` |
| `memory.searched` | Search executed | `{ type, query, results_count }` |
| `memory.deleted` | Data deleted | `{ type, key }` |
| `memory.error` | Operation failed | `{ type, operation, error }` |

---

## 8. Success Criteria

- [ ] `memory/` directory created with router + base
- [ ] All 7 store types wrap existing implementations under MemoryStore
- [ ] Agents call `memory.retrieve(ref)` instead of raw clients
- [ ] `MemoryRouter.search_all()` works across all stores
- [ ] All existing tests still pass
- [ ] Events emitted for every memory operation
