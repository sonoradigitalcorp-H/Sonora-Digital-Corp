# SPEC — Refactor a Arquitectura Multi-Tenant

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260722-001` |
| **Fecha** | 2026-07-22 |
| **Autor** | Mystic |
| **Tier** | 2 |
| **Estado** | draft |
| **Score requerido** | ≥60 |

## 1. Objetivo

Transformar `sonora-digital-corp/` de un monorepo plano a una arquitectura Core/Tenant donde el motor (core) nunca sabe quiénes son los clientes (tenants). Cada tenant define su identidad, conocimiento, herramientas y límites en archivos YAML/MD estandarizados, permitiendo escalar a decenas de clientes sin duplicar lógica y garantizando aislamiento total de datos.

## 2. Value Driver

founder-independence | automation | scalability | security

## 3. Functional Requirements

| FR# | Descripción |
|-----|-------------|
| FR1 | El Core (core/) no contiene referencias hardcodeadas a ningún cliente |
| FR2 | Cada tenant tiene su propio directorio en tenants/ con prompt.md, branding/, knowledge/, memory/, skills/, tools.yaml, mcp.yaml, policies.yaml, workflows/, config.yaml |
| FR3 | El TenantResolver carga dinámicamente el contexto del tenant en runtime (prompt, tools, MCP, policies) |
| FR4 | Las skills de Sonora no son accesibles desde tenants ajenos |
| FR5 | Qdrant usa colecciones separadas por tenant (tenant_${id}_memory) |
| FR6 | Neo4j usa databases separadas por tenant |
| FR7 | Postgres usa Row Level Security con tenant_id en cada tabla crítica |
| FR8 | El gateway identifica tenant_id antes de ruteo (webhook header, channel, o API key) |
| FR9 | Existe un tenants/_template/ para onboarding de nuevos clientes en < 5 minutos |
| FR10 | clients/ se depreca y archiva; todo nuevo cliente usa tenants/ |
| FR11 | Cada tenant puede tener su propio conjunto de skills (markdown) que el Core carga dinámicamente |
| FR12 | El Policy Engine valida cada acción contra tools.yaml y policies.yaml del tenant antes de ejecutar |

## 4. Success Criteria

- [ ] clients/ operativo con estructura estandarizada (prompt.md, tools.yaml, mcp.yaml, policies.yaml, config.yaml)
- [ ] tenants/sonora-digital/ migrado desde config actual
- [ ] tenants/abe-music/ migrado desde clients/abe-music/
- [ ] tenants/_template/ creado y listo para copiar
- [ ] TenantResolver implementado en core/tenants/
- [ ] Qdrant colecciones separadas por tenant verificadas
- [ ] Neo4j databases separadas por tenant verificadas
- [ ] Gateway identifica tenant por webhook/channel
- [ ] clients/ movido a archive/clients/ con README de deprecación
- [ ] `sdd test` pasa después de la migración

## 5. Gherkin Scenarios

Ver `gherkin/multi-tenant-platform.feature`

## 6. Edge Cases

- [EC1] Tenant sin tools.yaml definido: usar defaults del core con permisos mínimos
- [EC2] Tenant sin mcp.yaml: no conectar servidores MCP, solo tools nativas del core
- [EC3] Tenant con tenant_id inválido o desconocido: responder 403, no exponer estructura interna
- [EC4] Migración de clients/ existentes: mantener backward compatibility durante transición vía feature flag
- [EC5] Skills del core vs skills del tenant: si hay conflicto de nombres, gana la del tenant

## 7. Technical Approach

### Fase 1 — Foundation (Semana 1)
1. Crear `tenants/` con `_template/` (prompt.md, tools.yaml, mcp.yaml, policies.yaml, config.yaml)
2. Crear `core/tenants/resolver.go` (o `loader.py`) con lógica de TenantContext
3. Migrar `config/tenants.yaml` a `tenants/` como registro maestro

### Fase 2 — Migración AstroTech (Semana 2)
4. Migrar clients/ a estructura estandarizada (prompt.md, tools.yaml, mcp.yaml, policies.yaml, config.yaml)
5. Conectar TenantResolver al orchestrator loop
6. Verificar aislamiento de Qdrant collection + Neo4j database

### Fase 3 — Migración Sonora Digital + ABE (Semana 3)
7. Crear `tenants/sonora-digital/` y `tenants/abe-music/`
8. Mover skills globales a core/skills/ (no mezclar con tenants/)
9. Deprecar `clients/` → `archive/clients/`

### Fase 4 — Gateway & Seguridad (Semana 4)
10. Gateway identifica tenant por webhook header o channel
11. Policy Engine valida tools contra `tenants/*/policies.yaml`
12. Rate limiting por tenant

## 8. Dependencies

- OpenClaw orchestrator loop debe soportar carga dinámica de TenantContext
- Hermes debe leer prompt desde `tenants/{id}/prompt.md` y no desde config global
- Qdrant debe soportar colecciones dinámicas por tenant (CRUD de collections vía API)
- Neo4j debe soportar databases separadas o filtrado por tenant_id
- Postgres RLS debe configurarse por tabla crítica

## 9. Events to Emit

| Evento | Cuándo |
|--------|--------|
| `tenant.created` | Nuevo tenant creado desde template |
| `tenant.migrated` | Cliente migrado de clients/ a tenants/ |
| `tenant.config_updated` | Cambio en tools/mcp/policies de un tenant |
| `tenant.isolation_failed` | Intento de acceso cross-tenant detectado |

## 10. Kill Criteria

- Si después de 2 semanas no hay un tenant funcionando con el nuevo resolver, pausar y re-evaluar
- Si la migración rompe clients/ existentes sin recovery plan en < 2 horas, revertir

## 11. Scale Criteria

- Cuando se alcancen 5+ tenants activos, automatizar onboarding con script `bin/create-tenant`
- Cuando se alcancen 10+ tenants, implementar dashboard de administración de tenants
