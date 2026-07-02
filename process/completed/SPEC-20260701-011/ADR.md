# ADR-20260701-011 — MCP Tools Activos + Bloqueos Producción

## Context

Git MCP y Memory MCP estaban instalados pero ningún agente los usaba. Los bloqueos de Instagram, Wikipedia y TikTok handles son conocidos pero no estaban formalmente documentados.

## Decision

1. Agregar métodos git_status, git_commit, git_log, memory_search, memory_create_entities a HermesClient
2. Los 3 bloqueos son problemas de infraestructura, no de código. Documentarlos como conocidos.
3. Wikipedia 403 es permanente desde datacenter OVH — marcado como degraded.
4. Instagram login wall requiere cookies de sesión — no hay fix de código.
5. TikTok handles incorrectos en CEO data — documentados.

## Consequences

- Agentes futuros pueden hacer commits y buscar en memoria via HermesClient
- 5 nuevos tests para Git MCP y Memory MCP
- Bloqueos documentados, no silenciados
