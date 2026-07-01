# SPEC-20260630-007: Auth + MCP Gateway Unificado (Fase 1)

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260630-007` |
| **Fecha** | 2026-06-30 |
| **Autor** | Strategy OS |
| **Tier** | 2 |
| **Estado** | borrador |
| **Score requerido** | ≥60 |
| **ADR** | ADR-20260630-012 |

---

## 1. Objetivo

Migrar el entry point de SDC de nginx/FastAPI a MCP Gateway con auth OAuth 2.1, eliminando 3 de 4 capas de routing y estableciendo el CapabilityRegistry como runtime.

---

## 2. Value Driver

**founder-independence** — elimina la dependencia del fundador para configurar routing de nuevos agentes. **automation** — reduce de 4 a 1 la cantidad de capas que tocar para exponer un nuevo agente.

---

## 3. Functional Requirements

| FR# | Descripción |
|-----|-------------|
| FR1 | MCP Gateway debe autenticar todo request via Bearer JWT |
| FR2 | Los tokens JWT deben tener scope por capability (ej: `sales:read`) |
| FR3 | El gateway debe verificar rate limit por tenant en cada request |
| FR4 | El CapabilityRegistry debe resolver capability desde un task description |
| FR5 | nginx debe pasar de 9 location blocks a 1 solo proxy_pass |
| FR6 | Los 3 primeros routers FastAPI (sales, score, voice) deben tener equivalente MCP tool |
| FR7 | El SDK `sonora-client.js` debe gestionar tokens automáticamente |
| FR8 | Debe existir backward compatibility: FastAPI sigue funcionando durante migración |

---

## 4. Success Criteria

- [ ] `curl -X POST /api/auth/token -d '{"client_id":"sdc-core","client_secret":"..."}'` devuelve JWT válido
- [ ] `curl /api/tools -H "Authorization: Bearer <token>"` devuelve tools del scope
- [ ] `curl /api/tools -H "Authorization: Bearer <token_mal>"` devuelve 401
- [ ] `capability.resolve("generate a sales proposal")` devuelve `{capability: "sales", agent: "SalesAgent", confidence: 0.92}`
- [ ] nginx solo tiene 1 location block apuntando a `:18989`
- [ ] `sonora-client.js` puede autenticarse y llamar tools con token auto-gestionado
- [ ] Los endpoints FastAPI legacy siguen funcionando (compatibilidad)

---

## 5. Gherkin Scenarios

Ver `gherkin/SPEC-20260630-007.feature`

---

## 6. Edge Cases

- [EC1] Token expirado durante una tool call larga → renovación automática
- [EC2] Redis caído → auth falla abierto (deny) o cerrado (allow)? Decisión: deny (seguridad > disponibilidad)
- [EC3] Tenant no existe en `tenants.json` → rate limit default (free tier)
- [EC4] Capability no encontrada → fallback a research agent con log de warning
- [EC5] Misma capability solicitada concurrentemente → queue vs parallel? Decisión: parallel con rate limit por tenant

---

## 7. Technical Approach

### Auth Flow

```
Client                  MCP Gateway                     Redis
  │                         │                            │
  │ POST /api/auth/token    │                            │
  │ {client_id,secret}      │                            │
  │────────────────────────►│                            │
  │                         │ validate credentials       │
  │                         │───────────────────────────►│
  │                         │◄───────────────────────────│
  │ ◄───────────────────────│ {access_token, expires_in} │
  │                         │                            │
  │ POST /api/call          │                            │
  │ {tool, params}          │                            │
  │ Authorization: Bearer   │                            │
  │────────────────────────►│                            │
  │                         │ verify JWT + scope         │
  │                         │ check rate limit           │
  │                         │───────────────────────────►│
  │                         │◄───────────────────────────│
  │                         │ resolve capability         │
  │                         │ execute tool               │
  │ ◄───────────────────────│ {result}                   │
```

### JWT Payload

```json
{
  "sub": "sdc-core",
  "scope": "sales:read sales:write score:read",
  "tenant": "sdc-core",
  "iat": 1719700000,
  "exp": 1719703600,
  "jti": "uuid-unico"
}
```

### CapabilityRegistry Matching

1. Input task se embeddea via Qdrant
2. Se busca similaridad coseno contra capabilities registradas
3. Threshold mínimo: 0.75
4. Si no hay match: log + fallback a research

### Archivos nuevos a crear

| Archivo | Propósito |
|---------|-----------|
| `mcp/auth/jwt.js` | JWT sign/verify, RS256 key pair management |
| `mcp/auth/middleware.js` | Express middleware para auth + rate limit |
| `mcp/registry/capability-registry.js` | CapabilityRegistry runtime |
| `mcp/tools/sales.js` | MCP tools migradas de sales_router.py |
| `mcp/tools/score.js` | MCP tools migradas de score_router.py |
| `mcp/tools/voice.js` | MCP tools migradas de voice_router.py |

---

## 8. Dependencies

- Redis running (ya existe en Docker)
- Qdrant running (ya existe en Docker, para embeddings de capability matching)
- `capabilities/REGISTRY.md` actualizado con embeddings pre-computados
- `config/tenants.json` actualizado con client_id/client_secret
- OpenSSL o similar para generar key pair RS256

---

## 9. Events to Emit

| Evento | Cuando |
|--------|--------|
| `mcp_auth_granted` | Token emitido exitosamente |
| `mcp_auth_denied` | Credenciales inválidas |
| `mcp_auth_revoked` | Token revocado manualmente |
| `capability_registered` | Nueva capability en el registry |
| `capability_resolved` | Task → capability match exitoso |
| `capability_not_found` | Task sin capability match → fallback a research |
| `tool_executed` | Tool ejecutada exitosamente |
| `tool_failed` | Tool con error |
| `rate_limit_exceeded` | Rate limit excedido por tenant |

---

## 10. Kill Criteria

- Si después de 1 semana de desarrollo el auth middleware no está funcionando
- Si la migración de nginx rompe servicios de producción por más de 2 horas
- Si el equipo decide que MCP no es el estándar correcto

---

## 11. Scale Criteria

- Cuando haya más de 10 capabilities registradas → escalar a multi-gateway
- Cuando el auth supere 1000 tokens/minuto → añadir Redis cluster para denylist
- Cuando el capability registry supere 50 capabilities → añadir cache por capability type
