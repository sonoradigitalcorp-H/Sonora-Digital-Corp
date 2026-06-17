# Tasks: Memoria Persistente

---

## US1 — Almacenar y recuperar recuerdos (P1)

- [x] Implementar `src/core/neo4j_store.py` con CRUD de sesiones
- [x] Implementar `src/core/embeddings.py` (Ollama nomic-embed-text, 768d)
- [x] Implementar `src/core/rag.py` (Qdrant store + search + get_context)
- [x] Implementar MemoryAgent en `src/core/orchestrator.py` (store, recall, forget, list)
- [x] Driver Neo4j con fallback in-memory
- [x] Embeddings 768d en MCP server (`docker/mcp-server/embeddings.py`)
- [x] MCP tools con embeddings reales (`jarvis_search`, `jarvis_remember`, `jarvis_forget`)
- [x] Pipeline de chunking automático para documentos > 512 tokens

## US2 — Vincular conceptos en grafo (P2)

- [x] Extracción automática de entidades desde mensajes (NER via LLM + regex fallback)
- [x] Creación de relaciones entre conceptos en Neo4j
- [x] Query interface para temas relacionados
- [x] Tests para extracción y consulta de relaciones

## US3 — Gestionar sesiones (P1)

- [x] Schema Neo4j: Session + Message (constraints, indexes)
- [x] CRUD de sesiones via Neo4j (list, create, get, update, delete)
- [x] Pin/unpin sessions
- [x] Archive/unarchive sessions
- [x] Duplicate sessions
- [x] Export sessions (JSON, Markdown)
- [x] Full-text search en sesiones
- [x] Auto-guardar mensajes en sesión activa
- [x] Persistencia Neo4j con fallback in-memory
- [x] APIs REST en `webui/fastapp.py` (15 endpoints)
- [x] UI de gestión de sesiones en `webui/static/app.js`
- [x] Migrar sesiones legacy (formato anterior) a Neo4j — script en `scripts/migrate_legacy_sessions.py`

---

**Completado**: 23 tareas | **Pendiente**: 0 tareas
