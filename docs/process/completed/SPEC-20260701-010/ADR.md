# ADR-20260701-010 — Hermes Bridge Pattern + Memory MCP

| Campo | Valor |
|-------|-------|
| **ID** | `ADR-20260701-010` |
| **Fecha** | 2026-07-01 |
| **Spec** | `SPEC-20260701-010` |
| **Estado** | aceptado |

---

## Context

Los 3 agentes actuales (monitor, healer, notifier) se conectan directamente a Neo4j, Redis y Docker. Esto funciona pero no escala: cada nuevo agente necesita saber dónde está cada servicio. Crear un cliente MCP estándar resuelve esto para futuros agentes sin tocar los actuales.

## Decision

### 1. HermesClient como抽象

`apps/agents/hermes_client.py` envuelve llamadas MCP en métodos tipados: `call_tool()`, `query_neo4j()`, `search_qdrant()`, `health_status()`. Los agentes futuros solo importan `HermesClient` y llaman servicios sin conocer su ubicación.

### 2. Los 3 agentes actuales NO se modifican

Funcionan, están probados, y refactorizarlos solo por "pureza arquitectónica" introduce riesgo sin beneficio. Si en el futuro se rompen, se migran.

### 3. Memory MCP instalado

Disponible vía `npx @modelcontextprotocol/server-memory`. Sirve como grafo de conocimiento persistente para decisiones de agentes.

## Consequences

**Positivo:**
- 7 tests para HermesClient (success, timeout, unavailable, shortcuts)
- Memory MCP disponible para futuros agentes
- Sin cambios en agentes existentes
- CI verde

**Trade-offs:**
- HermesClient no se usa aún (los agentes actuales no lo llaman)
- Memory MCP no tiene consumidor todavía (se conectará en SPEC-011)

## Related

- Client: `apps/agents/hermes_client.py`
- Tests: `tests/agents/test_hermes_client.py`
- MCP: `npx @modelcontextprotocol/server-memory`
