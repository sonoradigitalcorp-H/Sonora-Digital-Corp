# Lección — SPEC-20260703-002

| Campo | Valor |
|-------|-------|
| **Spec** | `SPEC-20260703-002` |
| **Tier** | 3 |
| **Fecha** | 2026-07-03 |

---

## ¿Qué pasó?

Se creó BrainService para unificar 6 fuentes de conocimiento (Neo4j, Qdrant, Engram, Hermes state, eventos, lecciones) en un solo Knowledge Graph consultable via MCP tool + Web UI. Sync automático cada 30 min. 366 nodos creados.

---

## ¿Qué salió bien?

- [x] BrainService conecta a Neo4j + Qdrant + Engram sin error
- [x] 6 ingestores independientes — falla uno no rompe el resto
- [x] 5 integration tests pasan (connectivity, search, type filter, events, node count)
- [x] MCP tool registrado en Hermes config.yaml
- [x] Sync cron cada 30 min funcionando
- [x] Graceful degradation: si Neo4j falla → Qdrant → Engram → "no sé"
- [x] Web UI con FastAPI (3 endpoints) + dashboard HTML

---

## ¿Qué salió mal?

- [x] Qdrant version mismatch (client 1.18.0 vs server 1.7.4) — warning pero funciona
- [x] Engram db vacío (0 bytes) — no se perdieron datos, solo no seedeado
- [x] Truth ingestor clasifica servicios como personas (regex improvement needed)
- [x] Session.run() conflicto con parámetro `query` (renamed to `search_text`)
- [x] state/brain/dashboard.html no existía — error en scp por directory faltante

---

## ¿Qué haríamos diferente?

- Crear directorios antes de scp (verificar siempre el path remoto)
- Usar nombres de parámetros sin colisión con librerías externas
- Mejorar regex en truth ingestor: solo clasificar como PERSON si hay nombre de persona real
- No asumir stores poblados — Engram vacío debe manejarse explícitamente
- Documentar MCP tool inmediatamente después de crearla, no al final

---

## Engram Tags

brain, knowledge-graph, neo4j, qdrant, engram, mcp, fastapi, integration, dedup, cron
