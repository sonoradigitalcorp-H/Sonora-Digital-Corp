# SPEC — Unified Brain v2

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260703-002` |
| **Fecha** | 2026-07-03 |
| **Autor** | OpenClaw |
| **Tier** | 3 |
| **Estado** | completado |
| **Score requerido** | ≥60 |

---

## 1. Objetivo

Unificar Engram + Neo4j + Qdrant + Hermes state + eventos + lecciones en un solo cerebro consultable via MCP tool y Web UI, eliminando la fragmentación de conocimiento entre 4 stores diferentes.

---

## 2. Value Driver

Knowledge Impact + Founder Independence — cualquier agente pregunta una vez y obtiene respuesta desde la mejor fuente disponible, sin necesidad de saber dónde está cada store.

---

## 3. Functional Requirements

| FR# | Descripción |
|-----|-------------|
| FR1 | BrainService con conexiones a Neo4j, Qdrant, Engram verificadas |
| FR2 | 6 ingestores: engram, neo4j, events, hermes, lecciones, truth |
| FR3 | BrainSyncer con full sync + incremental + dedup |
| FR4 | MCP tool `unified_brain_query` con modo auto/semantic/graph/fts |
| FR5 | Web endpoints: /brain/search, /brain/stats, /brain/sync |
| FR6 | Sync cada 30 min via cron + healthcheck en health-monitor.sh |

---

## 4. Success Criteria

- [ ] BrainService conecta a Neo4j + Qdrant + Engram sin error
- [ ] 6 ingestores ejecutan sin error y producen ~365+ nodos en Neo4j
- [ ] MCP tool `unified_brain_query("Neo4j")` devuelve puerto 7687
- [ ] brain-sync.sh registrado en crontab (cada 30 min)
- [ ] MCP tool registrado en Hermes config.yaml
- [ ] 5 integration tests pasan

---

## 5. Gherkin Scenarios

Ver `gherkin/SPEC-20260703-002.feature`

---

## 6. Edge Cases

- Qdrant version mismatch (client 1.18.0 vs server 1.7.4) — warning but works
- Engram db vacío (0 bytes) en VPS — ingestor maneja graceful degradation
- Hermes state.db de 292MB — solo leer últimas 100 sesiones, no full scan
- Truth ingestor parsea TRUTH.md → puede crear personas donde no hay (regex improvement needed)

---

## 7. Technical Approach

Arquitectura en capas:

```
MCP Tool (unified_brain_query) ← Web UI (FastAPI)
        │
  BrainService (orquestador)
   ├── Neo4j (grafos + relaciones) :7687
   ├── Qdrant (vectores semánticos) :6333
   ├── Engram (memorias SQLite) state/engram.db
   └── Ingestors (6 fuentes → unifican a Knowledge nodes)
```

Sync incremental cada 30 min via cron. Cada ingestor es independiente, puede fallar sin romper el resto.

---

## 8. Dependencies

- Neo4j Docker (sdc-neo4j, puerto 7687)
- Qdrant Docker (sdc-qdrant, puerto 6333)
- state/engram.db existente (aunque vacío)
- /home/ubuntu/.hermes/state.db (292MB)
- Hermes events.jsonl generándose cada 15 min

---

## 9. Events to Emit

| Evento | Cuándo |
|--------|--------|
| `brain.service.created` | BrainService creado y conecta a stores |
| `brain.sync.completed` | Sync full/ incremental completado |
| `brain.sync.failed` | Sync falla en algún ingestor |
| `brain.query.executed` | Consulta via MCP tool ejecutada |
| `brain.dedup.merged` | Deduplicación fusiona nodos duplicados |

---

## 10. Kill Criteria

Si Neo4j o Qdrant no responden después de 3 intentos de reconexión — abortar deploy, diagnosticar containers Docker.

---

## 11. Scale Criteria

Cuando el brain tenga >10,000 nodos o >100 consultas/día, migrar a cluster Neo4j + Qdrant con HA.
