# ADR-012: Native Agent OS — MCP Gateway como Entry Point Único

| Campo | Valor |
|-------|-------|
| **ID** | `ADR-20260630-012` |
| **Fecha** | 2026-06-30 |
| **Estado** | propuesto |
| **Supersedes** | nginx-as-gateway (tácito) |

---

## Context

Sonora Digital Corp tiene actualmente **4 capas de enrutamiento**:

```
Request → nginx (:443) → FastAPI (:8000) → AgentOrchestrator → MCP Tools
                        → n8n (:5678)
                        → Telegram (:3003)
                        → Dashboard (:3001)
```

Problemas:
1. **4 fuentes de verdad de routing** — nginx location blocks, 21 FastAPI APIRouters, keyword rules del AgentOrchestrator, tool definitions de MCP
2. **Duplicación de lógica** — AgentOrchestrator keyword matching duplica FastAPI routers
3. **MCP no puede exponerse al exterior** — gateway en `:18989` sin auth
4. **Fricción para crear agentes** — hay que tocar 3 capas
5. **Routing por path/keywords, no por capability**

La constitución OMEGA v10.0 (ADR-011) define arquitectura agent-native. El Agent-OS.md describe un ecosistema MCP-gobernado. La infraestructura no refleja esa visión.

---

## Decision

**MCP Gateway se convierte en el entry point único**. nginx solo SSL termination. FastAPI solo web UI. AgentOrchestrator se migra a CapabilityRegistry runtime.

### Target

```
nginx (:443) → proxy_pass :18989
                   │
            Sonora MCP Gateway
                   │
            CapabilityRegistry
             ┌─────┼─────┐
             │     │     │
        MCP Tools  ADK   External
        (migrated) Agents MCP Servers
```

### Cambios por capa

| Capa | Cambio |
|------|--------|
| **nginx** | Solo SSL. Un `proxy_pass` a `:18989`. Eliminar 9 location blocks |
| **FastAPI** | Solo web UI. Deprecar 21 routers como API. Migrar a MCP tools |
| **AgentOrchestrator** | Reemplazar por CapabilityRegistry. Keyword → capability matching |
| **MCP Gateway (:18989)** | Entry point. +Auth OAuth 2.1, +CapabilityRegistry |
| **Hermes Bridge** | Conectar al gateway. Registrar como tool provider |
| **SDK** | `@sonora/sdk` apunta al gateway, no a FastAPI |

---

## Options Considered

| Opción | Pros | Contras |
|--------|------|---------|
| **A — MCP como entry point único** | 1 fuente de verdad, capability-based | Migración completa, breaking change temporal |
| **B — MCP en paralelo con nginx** | Bajo riesgo | Duplicación permanente, nunca se completa |
| **C — FastAPI como gateway MCP** | Mínimo cambio | No es MCP nativo, pierdes el estándar |

**Decisión: A**

---

## Consequences

### Positivas
- 1 capa de routing capability-based
- Agentes plug-and-play (ADK register → disponible)
- Exponer MCP con auth OAuth 2.1
- ~2,000 líneas de routing duplicado eliminadas
- Alineación con OMEGA v10.0

### Deuda técnica durante migración
- Coexistencia temporal FastAPI + MCP
- Clientes legacy hasta migrarse

---

## Fase 1: Auth + Gateway Unificado

### 1. Auth middleware en mcp-server-http.js

```
POST /api/auth/token → { access_token, expires_in, token_type: "Bearer" }
Todas las tools: Authorization: Bearer <token>, X-Tenant-ID: <tenant_id>
```

- JWT RS256, scopes por capability, revocación via Redis
- Rate limiting conectado a `check_rate_limit(tenant_id)`

### 2. CapabilityRegistry como servicio MCP

```
tool: capability.resolve → { capability, agent, confidence }
resource: capability://registry/list
```

- Runtime basado en `capabilities/REGISTRY.md`
- Matching semántico via embeddings en Qdrant
- Cache Redis TTL 60s

### 3. nginx simplification

```nginx
# ANTES: 9 location blocks
# DESPUÉS:
location / { proxy_pass http://127.0.0.1:18989; }
```

### 4. Primeros 3 routers migrados

| FastAPI Router | MCP Tool |
|---------------|----------|
| `sales_router.py` | `sonora:sales-*` |
| `score_router.py` | `sonora:enterprise-score` |
| `voice_router.py` | `sonora:voice-*` |

---

## Files Affected

| Archivo | Cambio |
|---------|--------|
| `mcp/gateway/mcp-server-http.js` | +Auth middleware, +CapabilityRegistry |
| `mcp/gateway/mcp-gateway.js` | +CapabilityRegistry integration |
| `infra/nginx/nginx-vps.conf` | Single proxy_pass |
| `infra/nginx/hermes.conf` | Eliminar location blocks API |
| `apps/webui/routes/sales_router.py` | Solo web UI, no endpoint público |
| `apps/webui/routes/score_router.py` | Idem |
| `apps/webui/routes/voice_router.py` | Idem |
| `apps/jarvis/src/core/orchestrator.py` | +CapabilityRegistry |
| `config/tenants.json` | +client_id/client_secret |
| `config/registry.json` | +capability mapping |
| `mcp/mcp-ecosystem.json` | +auth, +capability registry |
| `mcp/sdk/sonora-client.js` | +auth token management |

---

## Events

| Evento | Cuando |
|--------|--------|
| `mcp_auth_granted` | Token emitido |
| `mcp_auth_revoked` | Token revocado |
| `capability_registered` | Capability registrada |
| `capability_resolved` | Capability matched |
| `mcp_gateway_up` | Gateway health OK |

---

## Related

- `sonora-enterprise-os/prompts/prompts/OS/Agent-OS.md`
- `sonora-enterprise-os/capabilities/REGISTRY.md`
- `sonora-enterprise-os/adr/011-omega-architecture/spec.md`
- https://modelcontextprotocol.io/specification/2025-11-25/
