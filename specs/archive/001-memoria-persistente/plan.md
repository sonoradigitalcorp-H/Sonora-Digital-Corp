# Implementation Plan: Memoria Persistente

**Spec**: [spec.md](./spec.md)

---

## Technical Context

**Language/Version**: Python 3.10+, Go (opencode-go)
**Primary Dependencies**: neo4j, qdrant-client, ollama (nomic-embed-text), fastapi, uvicorn
**Storage**: Neo4j (grafos de sesiones/mensajes/recuerdos), Qdrant (vectores de embeddings), in-memory dict (fallback)
**Testing**: pytest con mocking de Neo4j/Qdrant

## Constitution Check

| Principio | Cómo lo cumple |
|-----------|---------------|
| Separación de responsabilidades | `neo4j_store.py` maneja persistencia, `rag.py` maneja búsqueda semántica, `MemoryAgent` orquesta |
| Privacidad y control | Todo corre local, datos sensibles en `.env` |
| Arquitectura modular | Neo4j, Qdrant y memoria son intercambiables via driver abstraction |
| Calidad y testing | Tests con mocking de servicios externos |

## Implementación

### Archivos existentes (ya implementados)

| Archivo | Propósito |
|---------|-----------|
| `docker/neo4j/Dockerfile` | Container Neo4j 5.19 + APOC |
| `docker/neo4j/init.cypher` | Schema inicial (Session, Message, Persona, Proyecto, Concepto) |
| `docker/neo4j/init_journey.cypher` | Schema alternativo + datos de ejemplo |
| `docker/qdrant/Dockerfile` | Container Qdrant v1.7.4 |
| `docker/qdrant/init_collections.py` | 4 colecciones 768d con payload indexes |
| `src/core/neo4j_store.py` | CRUD completo de sesiones con fallback in-memory |
| `src/core/embeddings.py` | Embeddings via Ollama nomic-embed-text (768d) |
| `src/core/rag.py` | Pipeline RAG: embed → Qdrant store → search → get_context |
| `src/core/orchestrator.py` | MemoryAgent con store/recall/forget/list |
| `webui/fastapp.py` | APIs REST de sesiones (list, create, get, update, delete, pin, archive, duplicate, export, search) |
| `docker/mcp-server/embeddings.py` | MCP Embedding service con auto-discovery Docker/native |
| `docker/mcp-server/server.py` | MCP tools: jarvis_search, jarvis_remember, jarvis_forget (con embeddings reales 768d) |

### Pendiente

| Tarea | Prioridad |
|-------|-----------|
| Pipeline de extracción de entidades desde mensajes para poblar el grafo Neo4j | P2 |
| Chunking de documentos largos antes de embed (hoy `rag.py` ya tiene `chunk_text`) | P2 |
| Query interface para navegar el grafo por relaciones | P2 |

## Archivos del spec

```
specs.new/001-memoria-persistente/
├── spec.md        # Este archivo
├── plan.md        # Este archivo
└── tasks.md       # Tareas
```
