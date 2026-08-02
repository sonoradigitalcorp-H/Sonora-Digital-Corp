# SPEC — Transformación a Plataforma SaaS Multi-Tenant de 4 Pilares

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260726-4PILARES` |
| **Fecha** | 2026-07-26 |
| **Autor** | SDD Orchestrator — Sonora Digital Corp |
| **Tier** | 3 |
| **Estado** | draft |
| **Score requerido** | ≥60 |

---

## 1. Objetivo

Transformar el monorepo de Sonora Digital Corp de un conjunto de herramientas integradas a una plataforma SaaS multi-tenant con 4 pilares (Productos, Capacidades, Agentes, Infraestructura) que permita escalar a cientos de clientes sin reescribir el core, manteniendo aislamiento total entre tenants y habilitando partners white-label con su propia marca, dominio y plan.

---

## 2. Value Driver

| Driver | Impacto |
|--------|---------|
| **Scalability** | De 5 clientes directos a cientos via partners sin reescribir |
| **Revenue** | Multi-tenant = múltiples planes (Starter $49 → Enterprise $999) + comisión partners |
| **Founder Independence** | Onboarding automático, aprovisionamiento por API, zero-touch operations |
| **Reusability** | Products reusan capabilities del core, agents orquestan capabilities |
| **Automation** | Pipeline completo: tenant onboard → DNS → deploy → billing → active |
| **Knowledge** | Engram aislado por tenant, datos nunca se mezclan |

---

## 3. Functional Requirements

| FR# | Descripción | Prioridad |
|-----|-------------|-----------|
| FR1 | **Estructura 4 Pilares**: El monorepo debe reflejar `products/`, `capabilities/`, `agents/`, `infra/` como capas independientes con imports unidireccionales (products → capabilities, agents → capabilities, nunca al revés) | P0 |
| FR2 | **Tenant Registry**: Cada tenant tiene `tenant_id`, `plan` (starter/pro/business/enterprise), `custom_domain`, `brand_config` (logo, colores, nombre), `channels` habilitados (whatsapp, telegram, web, voice), `features` por plan. Almacenado en Postgres + cache Redis | P0 |
| FR3 | **Aislamiento por Tenant**: Datos de cada tenant en Postgres con `tenant_id` en todas las tablas (RLS policy). Engram/Neo4j con prefijo o DB separada por tenant según plan. Qdrant con collection por tenant. Redis con namespace `tenant:{id}:*` | P0 |
| FR4 | **Capabilities Layer**: Auth (JWT multi-tenant), Memory (Engram 7 capas con tenant_id), AI (LLM router con rate-limit por plan), Voice (STT/TTS multi-tenant), Channels (WhatsApp, Telegram, Web, SMS como interfaces plugables), Payments (Stripe/MercadoPago con `tenant_id`), Analytics (eventos por tenant) | P0 |
| FR5 | **Agents Layer**: Sales Agent, Support Agent, Receptionist Agent, Accounting Agent, Marketing Agent — cada uno con harness (misión, skills, policies, memory scope) registrado en Agent Registry. Los agents orquestan capabilities, nunca productos directamente | P1 |
| FR6 | **Planes y Billing**: Starter ($49/mes), Pro ($149/mes), Business ($499/mes), Enterprise (custom). Cada plan define: # agents, # interactions, # clients, # channels, storage, features. Billing con Stripe, facturación automática, prorrateo, upgrades/downgrades, grace period 7 días | P1 |
| FR7 | **Partners White-Label**: Partners (como César/AztroTech) registrados con su propia marca, dominio custom, pricing propio. Comisión oculta SDC por transacción. El partner NO ve costos reales. Onboarding automatizado: `partner create → DNS → deploy → active` | P1 |
| FR8 | **Channels como Interfaces Intercambiables**: WhatsApp, Telegram, Web Widget, Voice son interfaces de una misma capability. Un tenant puede habilitar/deshabilitar canales según su plan. El agente recibe mensajes de cualquier canal y responde en el mismo | P1 |
| FR9 | **Marketplace de Agentes**: Partners y developers pueden crear, certificar y publicar agentes en el marketplace. Certificación automatizada (harness compliance, security scan, test suite). Revenue share: 80/20 (creator/SDC) | P2 |
| FR10 | **Gamificación Multi-Tenant**: Por tenant: XP, niveles, badges en su propio namespace. Logros globales SDC. Play/Work/Learn to Earn. Retos diarios. Todo aislado por `tenant_id` | P2 |

---

## 4. Success Criteria

- [ ] `GET /api/v1/tenants/:id` devuelve tenant con plan, dominio, canales, features
- [ ] Tenant A y Tenant B tienen datos completamente aislados (misma tabla Postgres, `WHERE tenant_id = X`)
- [ ] Partner César puede registrar su dominio `cesar.aztrotech.com`, poner su logo, y sus clientes no saben que existe SDC
- [ ] `POST /api/v1/tenants/:id/upgrade` cambia plan de Pro a Business con prorrateo
- [ ] Agent Sales puede invocar capability AI (LLM), capability Memory (Engram), capability Channel (WhatsApp) — todo con `tenant_id`
- [ ] `make eval` → structural tests pasan
- [ ] `make score` → ≥60
- [ ] `docker compose up` levanta el stack multi-tenant sin errores
- [ ] Stripe webhook crea tenant automáticamente al pagar

---

## 5. Gherkin Scenarios

Ver `process/active/gherkin/SPEC-20260726-4PILARES.feature`

---

## 6. Edge Cases

| EC# | Descripción | Mitigación |
|-----|-------------|------------|
| EC1 | **Tenant sin payment**: Se crea pero no paga → grace period 7 días, luego soft-lock (no eliminar datos) | Feature flags con `tenant.status = trial/suspended/active` |
| EC2 | **Partner se va**: César quiere irse con sus clientes → export data, periodo de transición 30 días, API de migración | `POST /api/v1/tenants/:id/export` genera dump |
| EC3 | **Cross-tenant data leak**: Error en RLS o en query sin `tenant_id` → dashboard de monitoreo con alertas de acceso cross-tenant | Tests de integración con 2 tenants, assertion de aislamiento |
| EC4 | **DNS conflict**: Dos partners quieren el mismo subdominio → validación única en DB, error descriptivo | Unique constraint en `tenants.custom_domain` |
| EC5 | **Rate-limit por tenant**: Un tenant satura la capability AI → `rate_limiter` por `tenant_id + plan`, cola de backpressure | Token bucket por tenant, cola Redis para overflow |
| EC6 | **Upgrade en medio del ciclo de facturación**: Pasa de Starter a Pro el día 15 → prorrateo, features se activan inmediatamente, siguiente cobro es el proporcional | `POST /api/v1/tenants/:id/upgrade` calcula prorate + factura |
| EC7 | **Degradación de servicio**: Si un tenant consume 10x su plan, no afecta a otros tenants → resource quotas por tenant (contenedor, CPU, memoria, conexiones DB) | cgroups/Pod resource limits + connection pooling por tenant |
| EC8 | **Data export masiva**: Un tenant con 1M registros pide export → async job con notificación | `POST /api/v1/tenants/:id/export` → job queue → email cuando listo |

---

## 7. Architecture

```
                    SONORA PLATFORM
                          │
     ┌────────────────────┼────────────────────┐
     │     PILLAR 1       │      PILLAR 2       │     PILLAR 3
     ▼                    ▼                      ▼
┌──────────────┐  ┌──────────────┐   ┌──────────────────┐
│  PRODUCTS    │  │ CAPABILITIES │   │    AGENTS        │
│  ──────────  │  │ ───────────  │   │  ────────────    │
│  CRM         │  │ Auth (JWT)   │   │  Sales Agent     │
│  Appointments│  │ Memory(Engram)│  │  Support Agent   │
│  Accounting  │  │ AI (LLM)     │   │  Receptionist    │
│  Ecommerce   │  │ Voice(STT/TTS)│  │  Orchestrator    │
│  Music       │  │ Channels     │   │  Accounting      │
│  Marketing   │  │ Payments     │   │  Marketing       │
│  Security    │  │ Analytics    │   │                  │
└──────┬───────┘  └──────┬───────┘   └────────┬─────────┘
       │                │                     │
       └──────────────┬─┴─────────────────────┘
                      │
                      ▼
            ┌─────────────────────┐
            │  PILLAR 4           │
            │  INFRASTRUCTURE     │
            │  ───────────────    │
            │  Docker / K8s       │
            │  Postgres + RLS     │
            │  Redis (namespace)  │
            │  Qdrant (per-col)   │
            │  Neo4j (per-DB)     │
            │  Monitoring         │
            │  CI/CD              │
            └─────────────────────┘

TENANT LANDSCAPE:
┌─────────────────────────────────────────────────────┐
│  TENANT A (SDC Direct)     │  TENANT B (Partner    │
│  ─────────────────         │  César - White Label) │
│  Plan: Business            │  ───────────────────  │
│  Domain: app.sonora.com    │  Plan: Partner Pro    │
│  Brand: Sonora             │  Domain: cesar.agency │
│  Channels: all             │  Brand: AztroTech     │
│  Agents: 5                 │  Channels: voice+wa   │
│  Clients: 50               │  Agents: 3            │
│  Billing: Stripe direct    │  Billing: via partner │
│                            │  SDC: hidden margin   │
└─────────────────────────────────────────────────────┘
```

### Imports Rule

```
products/   → capabilities/   ✅ (products consumen capabilities)
products/   → agents/         ❌ (products no llaman agents directamente)
agents/     → capabilities/   ✅ (agents orquestan capabilities)
agents/     → products/       ❌ (agents no conocen productos)
capabilities/ → infra/        ✅ (capabilities usan infra)
infra/      → nada            (infra no importa de nadie)
```

### Tenant Schema (Postgres)

```sql
CREATE TABLE tenants (
  tenant_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        TEXT NOT NULL,
  slug        TEXT UNIQUE NOT NULL,
  plan        TEXT NOT NULL CHECK (plan IN ('starter','pro','business','enterprise')),
  status      TEXT NOT NULL DEFAULT 'trial' CHECK (status IN ('trial','active','suspended','cancelled')),
  custom_domain TEXT UNIQUE,
  brand_config JSONB DEFAULT '{}',
  features    JSONB DEFAULT '{}',
  stripe_customer_id TEXT,
  stripe_subscription_id TEXT,
  created_at  TIMESTAMPTZ DEFAULT now(),
  trial_ends_at TIMESTAMPTZ DEFAULT now() + interval '7 days'
);
```

---

## 8. Dependencies

- Postgres 15+ con Row Level Security (RLS)
- Redis 7+ para rate-limiting, cache, session por tenant
- Qdrant para vectores (collection por tenant)
- Neo4j 5+ para grafos (database por tenant en Enterprise)
- Stripe Connect para billing multi-tenant
- Docker Compose + Docker Swarm o K8s para orquestación
- nginx con `server_name` dinámico para multi-dominio
- Cert-manager o acme.sh para SSL automático por dominio
- SDK de agents (harness registry, skill registry, policy engine)

---

## 9. Events to Emit

| Evento | Cuándo |
|--------|--------|
| `tenant.created` | Nuevo tenant registrado |
| `tenant.activated` | Tenant paga primer mes |
| `tenant.suspended` | Grace period expira sin pago |
| `tenant.upgraded` | Tenant cambia de plan |
| `tenant.downgraded` | Tenant baja de plan |
| `tenant.cancelled` | Tenant da de baja |
| `tenant.export.requested` | Tenant solicita export de datos |
| `tenant.export.completed` | Export listo para descargar |
| `partner.created` | Nuevo partner registrado |
| `agent.published` | Agent publicado en marketplace |
| `agent.installed` | Tenant instala agent del marketplace |
| `capability.rate_limited` | Tenant excede cuota de capability |

---

## 10. Kill Criteria

- Si después de 2 semanas no hay al menos 1 tenant externo (no SDC) activo y pagando
- Si el costo de infraestructura multi-tenant supera 3x el costo actual (monolito)
- Si la complejidad añadida bloquea entregas de producto por más de 1 sprint
- Si los tests de aislamiento cross-tenant fallan en CI (no hay tolerancia para data leaks)

---

## 11. Scale Criteria

- 10+ tenants activos → automatizar provisioning con script `scripts/provision-tenant.sh`
- 50+ tenants → dashboard de administración de tenants con métricas en vivo
- 100+ tenants → partitioning vertical (DB por región), sharding por tenant_id
- 500+ tenants → marketplace de agents abierto a third-party developers
- 1000+ tenants → agentes dedicados por tenant (contenedores aislados), K8s full auto-scaling
