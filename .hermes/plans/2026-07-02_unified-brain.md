# Unified Brain — Plan de Implementación

> **Goal:** Unificar todas las memorias fragmentadas (Engram, Neo4j, Qdrant, Hermes state, JSON files, eventos) en un solo "cerebro" consultable desde cualquier agente del sistema.

**Architecture:** Servicio central `BrainService` que (1) usa Neo4j como grafo de conocimiento maestro, (2) Qdrant para búsqueda semántica, (3) Engram para memoria jerárquica con decaimiento, y (4) expone una única MCP Tool `unified_brain_query` que cualquier agente (JARVIS, Hermes, OpenClaw) puede llamar. Incluye un pipeline de sincronización que ingiere datos de todas las fuentes existentes.

**Tech Stack:** Python, Neo4j (graph), Qdrant (vectors), SQLite/Engram (layered), MCP Tool interface, sentence-transformers (embeddings), cron para sync periódico.

---

## Fase 0: Estado Actual

### Data Stores Existentes

| Store | Tipo | Datos |
|-------|------|-------|
| **Engram** | SQLite + FTS5 | 52 memories, 7 layers (working→strategic) |
| **Neo4j** | Graph DB | 36 nodos: Service(15), Achievement(9), Spec(5), Person(3), Capability(3), Session(1) |
| **Qdrant** | Vector DB | 2 collections: abe-artists(5pts, dim7), abe-business(5pts, dim384) |
| **Hermes state.db** | SQLite + FTS5 | Sessions + messages con FTS5+trigram |
| **OpenClaw** | SQLite | 66 tablas de estado interno de agentes |
| **JSON files** | Archivos | 6 sesiones, rules.json, events.jsonl (61 eventos) |
| **Lecciones** | JSON | lecciones.json en products/ y constitution/ |

---

## Fase 1: Foundation — BrainService Core

### Task 1: Crear estructura BrainService

**Objective:** Scaffold del servicio central con configuración y conexiones a stores existentes

**Files:**
- Create: `apps/brain/__init__.py`
- Create: `apps/brain/config.py`
- Create: `apps/brain/service.py`

**config.py:**
```python
from pydantic import BaseSettings

class BrainConfig(BaseSettings):
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    engram_path: str = "state/engram.db"
    hermes_state_path: str = "/home/ubuntu/.hermes/state.db"
    embed_model: str = "all-MiniLM-L6-v2"
    collections_dir: str = "apps/brain/collections"

    class Config:
        env_prefix = "BRAIN_"
```

**service.py (scaffold):**
```python
class BrainService:
    def __init__(self, config: BrainConfig = None):
        self.config = config or BrainConfig()
        self.neo4j = None   # BoltDriver
        self.qdrant = None  # QdrantClient
        self.engram = None  # Engram instance
        self._connect()

    def _connect(self):
        from neo4j import GraphDatabase
        from qdrant_client import QdrantClient
        self.neo4j = GraphDatabase.driver(self.config.neo4j_uri, auth=(self.config.neo4j_user, self.config.neo4j_password))
        self.qdrant = QdrantClient(host=self.config.qdrant_host, port=self.config.qdrant_port)

    def close(self):
        if self.neo4j: self.neo4j.close()
```

**Verificación:** `python3 -c "from apps.brain.service import BrainService; b=BrainService(); print('ok')"`

---

### Task 2: Modelo de conocimiento unificado

**Objective:** Definir el schema de conocimiento que unifica todos los tipos de datos

**Files:**
- Create: `apps/brain/models.py`

```python
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

class KnowledgeType(str, Enum):
    SPEC = "spec"
    SERVICE = "service"
    PERSON = "person"
    ARTIST = "artist"
    SESSION = "session"
    MEMORY = "memory"
    RULE = "rule"
    EVENT = "event"
    LECCION = "leccion"
    ACHIEVEMENT = "achievement"
    CAPABILITY = "capability"

@dataclass
class KnowledgeNode:
    id: str
    type: KnowledgeType
    label: str
    summary: str
    details: dict = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    importance: int = 1       # 0-3
    embedding: Optional[list[float]] = None
    source: str = ""           # engram | neo4j | hermes | file | event
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class KnowledgeRelation:
    source_id: str
    target_id: str
    relation_type: str  # depends_on | contains | leads_to | related_to | implements
    weight: float = 1.0
```

---

### Task 3: MCP Tool — `unified_brain_query`

**Objective:** Exponer una herramienta MCP que cualquier agente pueda llamar para consultar el cerebro unificado

**Files:**
- Create: `apps/brain/mcp_tool.py`
- Modify: `apps/brain/service.py` (add query methods)

**Interfaz de la MCP Tool:**
```
Tool: unified_brain_query
Arguments:
  - query: str — texto de búsqueda
  - type: str (opcional) — filtrar por tipo (spec, service, person, artist, session, memory, rule, event, leccion, achievement, capability)
  - mode: str = "auto" — auto | semantic | graph | fts
  - limit: int = 10
  - min_importance: int = 0

Returns:
  - results: list[{id, type, label, summary, score, source, details}]
  - total: int
  - mode_used: str
```

**service.py — método unified_query:**
```python
def unified_query(self, query: str, type_filter: str = None, mode: str = "auto", limit: int = 10, min_importance: int = 0) -> dict:
    results = []
    mode_used = mode

    if mode == "auto":
        # Try semantic first, fallback to FTS, then graph
        results = self._semantic_search(query, type_filter, limit)
        if len(results) < 3:
            results = self._fts_search(query, type_filter, limit)
        if len(results) < 3:
            results = self._graph_search(query, type_filter, limit)
        mode_used = "semantic+fts+graph"
    elif mode == "semantic":
        results = self._semantic_search(query, type_filter, limit)
    elif mode == "fts":
        results = self._fts_search(query, type_filter, limit)
    elif mode == "graph":
        results = self._graph_search(query, type_filter, limit)

    if min_importance > 0:
        results = [r for r in results if r.get("importance", 0) >= min_importance]

    return {"results": results[:limit], "total": len(results), "mode_used": mode_used}

def _semantic_search(self, query, type_filter, limit):
    # Embed query → search Qdrant → enrich from Neo4j/Engram
    pass

def _fts_search(self, query, type_filter, limit):
    # Search Engram FTS5 + Hermes FTS5
    pass

def _graph_search(self, query, type_filter, limit):
    # Cypher MATCH on Neo4j with text contains
    pass
```

---

## Fase 2: Ingestión — Unificar todas las fuentes

### Task 4: Ingestor de Engram (52 memories)

**Files:**
- Create: `apps/brain/ingestors/engram_ingestor.py`

```python
class EngramIngestor:
    def ingest(self, brain: BrainService) -> int:
        conn = sqlite3.connect(brain.config.engram_path)
        cur = conn.execute("SELECT id, spec_id, tag, summary, context, importance, layer, timestamp FROM memories")
        count = 0
        for row in cur:
            node = KnowledgeNode(
                id=f"engram-{row[0]}",
                type=KnowledgeType.MEMORY,
                label=row[1] or "",
                summary=row[3],
                details={"context": row[4], "layer": row[6]},
                tags=row[2].split(",") if row[2] else [],
                importance=row[5],
                source="engram",
                created_at=parse_iso(row[7])
            )
            brain._index_node(node)
            count += 1
        conn.close()
        return count
```

### Task 5: Ingestor de Neo4j (36 nodos)

**Files:**
- Create: `apps/brain/ingestors/neo4j_ingestor.py`

```cypher
MATCH (n)
OPTIONAL MATCH (n)-[r]->(m)
RETURN n, labels(n), keys(n), collect({rel: type(r), target: id(m)})
```

Mapear labels → KnowledgeType:
- `Service` → SERVICE, `Spec` → SPEC, `Person` → PERSON, `Capability` → CAPABILITY, `Achievement` → ACHIEVEMENT, `Session` → SESSION

### Task 6: Ingestor de sesiones JSON (6 archivos)

**Files:**
- Create: `apps/brain/ingestors/session_ingestor.py`

Parsear `memory/learning/session-*.json` → KnowledgeNode(type=SESSION) con builds, broken, next_priorities, architecture en details.

### Task 7: Ingestor de eventos (events.jsonl)

**Files:**
- Create: `apps/brain/ingestors/events_ingestor.py`

Leer JSONL línea por línea → KnowledgeNode(type=EVENT), cada tipo de evento como label.

### Task 8: Ingestor de reglas (rules.json)

**Files:**
- Create: `apps/brain/ingestors/rules_ingestor.py`

Cada regla → KnowledgeNode(type=RULE) con confidence, violations, last_validated en details.

### Task 9: Ingestor de lecciones (lecciones.json)

**Files:**
- Create: `apps/brain/ingestors/lecciones_ingestor.py`

Leer ambos archivos `products/yami/memory/lecciones.json` y `constitution/memory/lecciones.json`.

### Task 10: Ingestor de Hermes state.db

**Files:**
- Create: `apps/brain/ingestors/hermes_ingestor.py`

Extraer sesiones recientes y mensajes destacados de Hermes state.db.

---

## Fase 3: Sincronización y Mantenimiento

### Task 11: Brain Sync Pipeline

**Files:**
- Create: `apps/brain/sync.py`

```python
class BrainSyncer:
    def __init__(self, brain: BrainService):
        self.brain = brain
        self.ingestors = [
            EngramIngestor(),
            Neo4jIngestor(),
            SessionIngestor(),
            EventsIngestor(),
            RulesIngestor(),
            LeccionesIngestor(),
        ]

    def full_sync(self) -> dict:
        results = {}
        for ingestor in self.ingestors:
            name = ingestor.__class__.__name__
            try:
                count = ingestor.ingest(self.brain)
                results[name] = {"status": "ok", "count": count}
            except Exception as e:
                results[name] = {"status": "error", "error": str(e)}
        return results

    def incremental_sync(self):
        # Only new/changed items since last sync
        pass
```

### Task 12: Cron de sync automático

**Files:**
- Modify: `scripts/close-session.sh` (add brain sync step)
- Create: `scripts/brain-sync.sh` (standalone cron script)

```bash
#!/bin/bash
# brain-sync.sh — Sync all sources into Unified Brain
cd /home/ubuntu/sonora-digital-corp
python3 -m apps.brain.sync_cli full-sync
echo "Brain synced at $(date)" >> state/brain-sync.log
```

Registrar en crontab: `*/30 * * * * /home/ubuntu/sonora-digital-corp/scripts/brain-sync.sh`

---

## Fase 4: Unified Brain MCP — Integración con Agentes

### Task 13: Registrar MCP Tool en el Gateway

**Files:**
- Modify: `apps/brain/mcp_tool.py` (completar implementación)
- Modify: gateway config o script de registro

Registrar `unified_brain_query` como tool MCP accesible por:
- JARVIS (via MCP bridge)
- Hermes (via tool call)
- OpenClaw (via gateway)
- Telegram bot

### Task 14: Web UI para el Brain

**Files:**
- Create: `apps/brain/web.py` (FastAPI router)
- Create: `state/brain/dashboard.html` o integrar en AGENTIC OS Dashboard

Endpoints:
- `GET /brain/search?q=<query>` — búsqueda pública
- `GET /brain/stats` — estadísticas del cerebro (total nodos, tipos, últimas sync)
- `POST /brain/ingest` — trigger manual de sync

---

## Fase 5: Auto-aprendizaje

### Task 15: Brain Learning Loop

**Files:**
- Create: `apps/brain/learning.py`

Cuando un agente hace una query y elige un resultado:
- Incrementar `access_count` en el nodo
- Si un nodo se accede frecuentemente, promover su importancia
- Si hay relaciones implícitas (misma query → siempre mismo par de resultados), crear arista

### Task 16: Deduplicación

**Files:**
- Create: `apps/brain/dedup.py`

Detectar nodos duplicados por:
- Mismo label + tipo + source similar
- Embedding cosine similarity > 0.95
- Mismo spec_id o tag

Unir: fusionar details, sumar access_counts, mantener la más reciente.

---

## Verificación y Tests

### Task 17: Tests del Brain

**Files:**
- Create: `tests/brain/test_unified_query.py`
- Create: `tests/brain/test_ingestors.py`
- Create: `tests/brain/test_sync.py`

Test targets:
```bash
python3 -m pytest tests/brain/ -v --cov=apps.brain
```

Casos:
1. Query semántica encuentra memory correcta
2. Query FTS encuentra por tag
3. Query grafo encuentra relaciones
4. Ingestor de Engram importa 52 memorias
5. Ingestor de Neo4j importa 36 nodos
6. Sync full no duplica
7. Dedup fusiona duplicados correctamente

---

## Resumen de Archivos a Crear/Modificar

| Archivo | Acción |
|---------|--------|
| `apps/brain/__init__.py` | Crear |
| `apps/brain/config.py` | Crear |
| `apps/brain/models.py` | Crear |
| `apps/brain/service.py` | Crear |
| `apps/brain/mcp_tool.py` | Crear |
| `apps/brain/sync.py` | Crear |
| `apps/brain/learning.py` | Crear |
| `apps/brain/dedup.py` | Crear |
| `apps/brain/web.py` | Crear |
| `apps/brain/ingestors/__init__.py` | Crear |
| `apps/brain/ingestors/engram_ingestor.py` | Crear |
| `apps/brain/ingestors/neo4j_ingestor.py` | Crear |
| `apps/brain/ingestors/session_ingestor.py` | Crear |
| `apps/brain/ingestors/events_ingestor.py` | Crear |
| `apps/brain/ingestors/rules_ingestor.py` | Crear |
| `apps/brain/ingestors/lecciones_ingestor.py` | Crear |
| `apps/brain/ingestors/hermes_ingestor.py` | Crear |
| `scripts/brain-sync.sh` | Crear |
| `tests/brain/test_unified_query.py` | Crear |
| `tests/brain/test_ingestors.py` | Crear |
| `tests/brain/test_sync.py` | Crear |
| `scripts/close-session.sh` | Modificar (añadir brain sync) |

---

## Riesgos y Tradeoffs

| Riesgo | Mitigación |
|--------|-----------|
| Embeddings requieren GPU | Usar `all-MiniLM-L6-v2` (CPU, 80MB, ~50ms/embedding) |
| Qdrant dimension mismatch | Normalizar todas a dim=384 (o usar colección unificada) |
| Datos duplicados entre stores | Dedup post-sync con cosine similarity |
| Latencia en queries multi-store | Cache local en SQLite + queries paralelas con asyncio |
| Dependencia de 3 stores (Neo4j+Qdrant+SQLite) | BrainService con health check y fallback degradation |

## Open Questions

1. ¿Embeddings con modelo local o API externa? → Propongo `sentence-transformers/all-MiniLM-L6-v2` local
2. ¿Unificar Qdrant en 1 colección o mantener separadas? → 1 colección `brain-knowledge` con payload de tipo
3. ¿Sincronización full o incremental? → Full en primera ejecución, incremental cada 30 min
