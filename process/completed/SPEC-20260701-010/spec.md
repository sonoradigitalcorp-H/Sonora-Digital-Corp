# SPEC — Hermes Bridge Pattern + Memory MCP

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260701-010` |
| **Fecha** | 2026-07-01 |
| **Autor** | OpenClaw |
| **Tier** | 2 |
| **Estado** | activo |
| **Score requerido** | ≥60 |

---

## 1. Objetivo

Crear un cliente MCP estándar para futuros agentes y conectar Memory MCP al ecosistema para que los agentes recuerden decisiones entre reinicios. Los 3 agentes actuales (monitor, healer, notifier) NO se modifican — funcionan bien con conexiones directas.

---

## 2. Value Driver

knowledge, automation, scalability

---

## 3. Functional Requirements

| FR# | Descripción |
|-----|-------------|
| FR1 | `apps/agents/hermes_client.py` — cliente MCP que envuelve llamadas a Hermes |
| FR2 | El cliente expone métodos: `call_tool()`, `query_neo4j()`, `search_qdrant()`, `health_status()` |
| FR3 | Memory MCP instalado y configurado como servidor MCP |
| FR4 | OpenClaw (AGENTS.md) documentado con herramientas disponibles |
| FR5 | Tests mock para hermes_client |

---

## 4. Success Criteria

- [ ] `hermes_client.call_tool("neo4j_query", ...)` funciona
- [ ] Memory MCP responde a `search_nodes`
- [ ] Tests pasan en CI
- [ ] Documentación actualizada

---

## 5. Technical Approach

```
apps/agents/hermes_client.py
  └─ class HermesClient
       ├─ call_tool(name, params) → MCP tool call via Hermes
       ├─ query_neo4j(cypher) → shortcut para gateway_call  
       ├─ search_qdrant(collection, vector) → shortcut
       └─ health_status() → check all services
```

Memory MCP: instalado via `npx @modelcontextprotocol/server-memory`.
Los agentes FUTUROS usarán `HermesClient` en vez de conexiones directas.

---

## 6. Dependencies

- Hermes MCP funcionando en :8000 ✅
- MCP SDK 1.28.1 ✅
- Node.js disponible para npx ✅

---

## 7. Events to Emit

| Evento | Cuándo |
|--------|--------|
| `hermes_client_ready` | Cliente MCP creado |
| `memory_mcp_connected` | Memory MCP instalado |

---

## 8. Kill Criteria

Si Hermes no responde en :8000, el cliente debe fallar graceful y loguear warning.

---

## 9. Scale Criteria

- Auto-descubrimiento de tools vía Hermes
- Cache de tools disponibles
- Fallback a conexión directa si Hermes no responde
