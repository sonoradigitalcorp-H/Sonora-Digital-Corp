# ADR-20260726-4PILARES — Arquitectura Multi-Tenant de 4 Pilares

| Campo | Valor |
|-------|-------|
| **ID** | `ADR-20260726-4PILARES` |
| **Fecha** | 2026-07-26 |
| **Spec** | `SPEC-20260726-4PILARES` |
| **Estado** | propuesto |

---

## Context

Sonora Digital Corp comenzó como un monorepo con `apps/`, `products/`, `clients/` donde los límites eran borrosos: productos importaban directamente de apps, clients tenían código en apps/core, y no existía un concepto de tenant. Con la llegada de partners como César (AztroTech, $1M/mes potencial) y la necesidad de escalar a múltiples clientes con marcas, dominios y planes distintos, la arquitectura actual no puede sostener el crecimiento.

Problemas detectados:
- **Sin aislamiento**: Todos los datos en las mismas tablas, no hay `tenant_id`
- **Sin planes**: No hay concepto de plan, todos tienen el mismo nivel de servicio
- **Sin white-label**: Partners no pueden tener su propia marca/dominio
- **Acoplamiento**: products importan de apps, no hay separación clara capabilities/agents
- **Onboarding manual**: Cada nuevo tenant requiere intervención del founder

---

## Decision

Adoptar una **arquitectura de 4 pilares** con multi-tenant nativo:

1. **Products** → Lo que se vende (CRM, appointments, accounting, ecommerce, music, marketing, security)
2. **Capabilities** → Lo que los products y agents consumen (auth, memory, AI, voice, channels, payments, analytics)
3. **Agents** → Quienes orquestan capabilities (sales, support, receptionist, orchestrator, accounting, marketing)
4. **Infrastructure** → Donde corre todo (Docker, Postgres+RLS, Redis namespace, Qdrant collection, Neo4j, monitoring)

Regla de imports: `products → capabilities`, `agents → capabilities`, `capabilities → infra`. Prohibido: `capabilities → products`, `agents → products`.

Multi-tenant se implementa con:
- **Postgres RLS**: `tenant_id` en cada tabla, policies de aislamiento
- **Redis namespaces**: `tenant:{id}:*`
- **Qdrant collections**: una por tenant, creada automáticamente
- **Neo4j databases**: una por tenant (Enterprise) o property prefix

---

## Options Considered

| Opción | Pros | Contras |
|--------|------|---------|
| **A. 4 Pilares + RLS** (elegida) | Separación clara, RLS es estándar Postgres, bajo overhead, migrations simples | Requiere refactor grande inicial |
| **B. Database-per-tenant** | Aislamiento total, backup granular | Complex: migrations N veces, conex pool por DB, costoso en < 100 tenants |
| **C. Schema-per-tenant** | Aislamiento medio, migrations manejables | Postgres no escala bien con 1000+ schemas, queries cross-tenant imposibles |
| **D. Mantener monorepo actual + tenant_id ad-hoc** | Sin refactor | Caos asegurado: sin boundaries claros, products y capabilities mezclados, escala a 5 clients max |

---

## Consequences

**Positivas**:
- Escalabilidad vertical y horizontal: de 5 a 1000+ tenants
- Partners white-label sin límite: cada uno con su marca y pricing
- Onboarding zero-touch: API crea tenant, DNS, SSL, todo automático
- Marketplace de agents como nueva fuente de revenue (80/20)
- Aislamiento real: RLS + namespace + collection garantizan que un tenant no ve datos de otro
- New capabilities se añaden sin afectar products existentes

**Riesgos**:
- Refactor grande: migrar `apps/` a `capabilities/` puede romper cosas existentes
- RLS mal configurado = data leak (mitigación: tests de integración cross-tenant en CI)
- Complejidad operativa: monitorear N tenants requiere dashboards nuevos
- Stripe Connect + billing multi-tenant tiene edge cases (prorrateo, grace period, dunning)
- Partners pueden intentar bypassear la plataforma una vez que entienden el stack

**Mitigaciones**:
- Sprint 1 y 2 mantienen compatibilidad hacia atrás (no romper nada existente)
- Tests de aislamiento cross-tenant bloquean el CI si fallan
- Script de provisionamiento auditado, no expone secrets al partner
- La comisión se deduce ANTES de que el partner vea el revenue
- Los datos y la memoria viven en SDC, no en el partner (vendor lock-in positivo)

---

## Lessons

- El monorepo actual es funcional para 5-10 clients, pero no escala más allá
- La separación products/capabilities/agents es natural en el código existente (solo hay que formalizarla)
- RLS en Postgres es la solución más pragmática para multi-tenant en este stage (database-per-tenant sería premature optimization)
- Stripe Connect es más complejo que Stripe normal pero necesario para partners white-label
- OMEGA-PROMPT exige founder independence — esta arquitectura la logra con zero-touch onboarding

---

## Related

- Spec: `process/active/SPEC-20260726-4PILARES.md`
- Plan: `process/active/plan-4PILARES.md`
- Tasks: `process/active/tasks-4PILARES.md`
- Gherkin: `process/active/gherkin/SPEC-20260726-4PILARES.feature`
- Score: `process/active/SCORE-20260726-4PILARES.md`
- Events: `process/active/EVENTS-4PILARES.md`
- Previous ADR: `ADR-20260726-ECOSYSTEM`
- OMEGA-PROMPT: `kernel/OMEGA-PROMPT.md`
