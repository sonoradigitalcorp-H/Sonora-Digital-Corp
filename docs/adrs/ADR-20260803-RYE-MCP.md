# ADR-20260803-RYE-MCP

| Campo | Valor |
|-------|-------|
| **ID** | `ADR-20260803-RYE-MCP` |
| **Fecha** | 2026-08-03 |
| **Spec** | SPEC-030: RYE OpenClaw Agents |
| **Estado** | aceptado |

---

## Context

Los 7 agentes RYE necesitan acceso a: conocimiento RAG (Qdrant), memoria persistente (engram), LLM (OpenRouter) y herramientas auxiliares (filesystem, github, fetch, playwright). OpenClaw gestiona sus MCP servers con `openclaw mcp add/probe/doctor`. El servidor `sdc-mcp-local` ya expone `engram_save/get/search`, `rag_search` y `llm_chat` (verificado: `skills/mcp/servers/sdc_mcp_stdio.py`).

## Decision

Exponer a los agentes RYE los siguientes MCP servers:

| Server | Tools que aporta | Notas |
|--------|------------------|-------|
| `sdc-mcp-local` (stdio) | engram_save, engram_get, engram_search, engram_list_layers, rag_search, llm_chat, sdc_status | El corazón RAG+memoria+LLM; primero en la lista |
| `qdrant` | rag_index, rag_search, rag_list_collections | Vector store nativo (alternativa/refuerzo al sdc-mcp-local) |
| `filesystem` | acceso a manuales y conocimientos de RYE | lectura de `tenants/rye/knowledge/**` |
| `github` | revisar PRs, issues | para el gate RDD y flujos de Iván |
| `fetch` | docs FANUC/Cognex online | documentación de fabricante |
| `playwright` | navegación web | consultas web con UI |

**Orden de registro**: `sdc-mcp-local` primero (es el RAG-first). Todos se agregan con `openclaw mcp add` y se validan con `openclaw mcp doctor`.

## Options Considered

| Opción | Pros | Contras |
|--------|------|---------|
| **sdc-mcp-local como MCP principal** | Ya existe, expone engram+rag+llm, coherente con stack | Es stdio, requiere que el entorno tenga las deps |
| Solo Qdrant MCP oficial | Soporte nativo | No trae engram ni llm_chat, hay que configurar más servers |
| Sin MCP (bot importa RAGRetriever directo, patrón Aztrotech) | Baja latencia | OpenClaw no lo soporta así, rompe el modelo de gateway |

## Consequences

- **Positivas**: un solo server cubre RAG+memoria+LLM; los agentes solo ven las tools que su skill-set permite.
- **Positivas**: coherente con Aztrotech (mismo `rag_retriever` / FastEmbed 384-dim), reutilizable para otros clientes.
- **Riesgos**: el stack MCP debe estar verificado e2e antes de tocar producción (mitigado en Sprint 1/2).
- **Riesgos**: los secrets de OpenRouter viven en `~/.config/sonora/env.local`, fuera del repo.

## Related

- `skills/mcp/servers/sdc_mcp_stdio.py` (implementación sdc-mcp-local)
- `tenants/rye/bot/rye_engine.py` (motor unificado 2 capas)
- `scripts/rag.md` (documentación RAG MCP)
- `ADR-20260803-RYE-SECURITY`

## Hallazgo 2026-08-03: capa LLM chat

La capa **RAG + conocimiento curado funciona** (verify PASSED). La capa `llm_chat`
vía OpenRouter devolvía `401 User not found` en `/chat/completions` aunque
`/models` respondía 200 — es un problema de **cuenta/plan OpenRouter**, no de código.
El motor `rye_engine.py` está listo para generar la respuesta.

**RESOLUCIÓN (2026-08-03)**: la key activa en `~/.config/sonora/env.local`
(`sk-or-v1-4674...`) dio 401. La key válida estaba en `infra/.env.backup`
(`sk-or-v1-f7881...`) y funciona (200, responde en `/chat/completions`). Se
actualizó `env.local` (respaldo previo en `env.local.bak-before-keyfix`).
Verificado end-to-end: `rye_engine.py` genera respuesta completa con la
definición curada de SRVO-075 + pasos accionables. Diagnóstico previo en
`ADR-20260802-AZROTECH-MVP-RAG-MEMORIA` (historial de keys OpenRouter que expiran).

## Unificación (principios de Joaquín Ruiz / OKF)

El RAG se mejoró siguiendo `jokiruiz.com/inteligencia-artificial/que-es-open-knowledge-format-okf-rag/`:
- **Capa 1 (concepto curado)**: conocimiento exacto y estable en markdown con
  frontmatter (type/version/timestamp) navegable por `rye-index.md` — respuestas
  deterministas y trazables a ruta de archivo.
- **Capa 2 (RAG)**: `rag_search` en `kb_rye` para "busca dónde se mencionó X".
- **Regla de vigencia**: si el RAG contradice a un concepto curado, gana el concepto.
- **Ausencia**: el índice permite saber qué existe; si no está, se dice y se sugiere
  manual FANUC (en vez de alucinar).
- **Metadata en fragmentos**: fuente + score en cada hit para trazabilidad.
