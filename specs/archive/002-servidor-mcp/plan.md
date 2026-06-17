# Implementation Plan: Servidor MCP

**Spec**: [spec.md](./spec.md)

---

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: fastmcp, neo4j, qdrant-client, requests, httpx
**Architecture**: Servidor FastMCP dockerizado + módulo Python `src/core/tools.py` para function calling local
**Testing**: pytest con mocking de servicios externos

## Constitution Check

| Principio | Cómo lo cumple |
|-----------|---------------|
| Separación de responsabilidades | `tools.py` (local) y `server.py` (MCP) son independientes |
| Seguridad por defecto | Whitelist de comandos, validación de rutas de archivo |
| Arquitectura modular | Cada tool es una función independiente y reemplazable |
| Calidad y testing | Tests unitarios para cada tool con casos de error |

## Implementación

### Archivos existentes

| Archivo | Propósito |
|---------|-----------|
| `docker/mcp-server/Dockerfile` | Multi-stage Docker build con HEALTHCHECK |
| `docker/mcp-server/server.py` | 10 MCP tools con embeddings reales (768d) |
| `docker/mcp-server/embeddings.py` | Wrapper Ollama con auto-discovery Docker/native |
| `docker/mcp-server/config.py` | Config con env fallbacks |
| `docker/mcp-server/requirements.txt` | Dependencias |
| `src/core/tools.py` | 10 LLM tools + function calling router + whitelist |
| `src/core/orchestrator.py` | SkillAgent con catálogo de 8 skills + run + docs |

### Pendiente

| Tarea | Prioridad |
|-------|-----------|
| Rate limiting en web_fetch | P2 |
| Cache de resultados frecuentes (Redis o in-memory) | P2 |
| Executor para la tool `ask_user` (tiene schema pero no función) | P2 |

## Archivos del spec

```
specs.new/002-servidor-mcp/
├── spec.md
├── plan.md
└── tasks.md
```
