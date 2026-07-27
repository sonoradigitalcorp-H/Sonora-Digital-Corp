# Tasks — Transformación 4 Pilares Multi-Tenant

Estimación: `[S]` = small (2-4h), `[M]` = medium (1-2d), `[L]` = large (3-5d), `[XL]` = extra large (1+ semanas)

---

## Sprint 1: Products + Capabilities (Semanas 1-2)

### 1.1 Estructura de directorios

- [ ] `[M]` Crear directorios: `capabilities/`, `agents/`, mover `infra/` existente a Pilar 4
- [ ] `[S]` Crear `capabilities/__init__.py`, `capabilities/auth/`, `capabilities/memory/`, `capabilities/ai/`, `capabilities/voice/`, `capabilities/channels/`, `capabilities/payments/`, `capabilities/analytics/`
- [ ] `[M]` Mover código actual de `apps/core/` a `capabilities/` preservando git history
- [ ] `[S]` Actualizar `pyproject.toml` con namespace packages: `sonora.products`, `sonora.capabilities`, `sonora.agents`, `sonora.infra`
- [ ] `[M]` Crear `products/__init__.py` con ProductBase class y registry
- [ ] `[S]` Migrar `products/registry.yaml` a productos reales en `products/`

### 1.2 Capabilities Layer

- [ ] `[M]` **Auth Capability**: JWT multi-tenant con `tenant_id` en payload, middleware de verificación
- [ ] `[M]` **Memory Capability**: Engram wrapper con `tenant_id` en todas las queries, FTS5 aislado
- [ ] `[M]` **AI Capability**: LLM router multi-tenant con rate-limit por plan, fallback provider
- [ ] `[M]` **Channels Capability**: Interfaz abstracta `Channel` + implementaciones `WhatsAppChannel`, `TelegramChannel`, `WebChannel`, `VoiceChannel`
- [ ] `[S]` **Payments Capability**: Stripe/MercadoPago integración con `tenant_id`
- [ ] `[S]` **Analytics Capability**: Eventos con `tenant_id`, dashboard básico
- [ ] `[M]` Tests de capabilities: test_auth_multi_tenant, test_memory_isolation, test_ai_rate_limit
- [ ] `[S]` `make eval` pasa para capabilities

### 1.3 Products Refactor

- [ ] `[M]` Migrar productos existentes (`products/mystika/`, `products/clon-digital/`, etc.) a nuevo base class
- [ ] `[S]` Cada producto importa de `capabilities/*` en lugar de `apps/*`
- [ ] `[S]` Tests de productos pasan con nueva estructura

---

## Sprint 2: Agents + Orchestrator + Flujos (Semanas 3-4)

### 2.1 Agent Harness SDK

- [ ] `[L]` Crear `agents/sdk/` con: `HarnessBase`, `SkillRegistry`, `PolicyEngine`, `MemoryScope`
- [ ] `[M]` Agente registro: `agents/registry.yaml` con harness, skills, policies por agente
- [ ] `[M]` Cada harness define: misión, inputs, outputs, events, metrics, failure modes
- [ ] `[M]` Event-driven: cada agente emite eventos (`agent.started`, `agent.completed`, `agent.failed`)
- [ ] `[S]` Tests del SDK

### 2.2 Agents Canónicos (5)

- [ ] `[M]` **Sales Agent** (`agents/sales/`): pipeline leads, calificación, propuestas, cierre
- [ ] `[M]` **Support Agent** (`agents/support/`): tickets, SLAs, resoluciones, escalaciones
- [ ] `[M]` **Receptionist Agent** (`agents/receptionist/`): inbound calls, routing, mensajes
- [ ] `[M]` **Accounting Agent** (`agents/accounting/`): facturación, cobros, reportes
- [ ] `[M]` **Marketing Agent** (`agents/marketing/`): campañas, social media, analytics
- [ ] `[S]` Tests de agents: happy path + edge cases

### 2.3 Orchestrator Engine

- [ ] `[L]` Crear `agents/orchestrator/`: engine que recibe eventos, decide qué agent activar
- [ ] `[M]` Policy engine: reglas de routing (qué agente maneja qué tipo de solicitud)
- [ ] `[S]` Cola de eventos con backpressure por tenant
- [ ] `[M]` Workflow definitions: `workflows/` con DAGs de agentes (ej: lead → sales → accounting)
- [ ] `[S]` Tests de orquestación multi-tenant

---

## Sprint 3: Tenants + Branding + Plans + Billing + Partners (Semanas 5-6)

### 3.1 Tenant Registry

- [ ] `[L]` Crear `capabilities/tenants/`: CRUD de tenants, plan management, feature flags
- [ ] `[M]` API REST: `GET/POST/PUT /api/v1/tenants`, `GET /api/v1/tenants/:id`, `POST /api/v1/tenants/:id/upgrade`
- [ ] `[M]` RLS policies en Postgres: todas las tablas tienen `tenant_id`, policies de aislamiento
- [ ] `[M]` Cache en Redis: `tenant:{id}:config` TTL 300s, invalidación on change
- [ ] `[M]` Multi-dominio: nginx virtual hosts dinámicos, SSL automático por tenant
- [ ] `[S]` Script `scripts/provision-tenant.sh <name> <plan> <domain>`
- [ ] `[L]` Tests de integración cross-tenant: Tenant A no puede ver datos de Tenant B
- [ ] `[S]` `make eval` pasa para tenants

### 3.2 Plans y Billing

- [ ] `[M]` Definir planes en `config/plans.yaml`: Starter, Pro, Business, Enterprise
- [ ] `[S]` Cada plan define: agents, interactions, clients, channels, storage, features
- [ ] `[M]` Stripe Connect: webhooks `checkout.session.completed`, `invoice.paid`, `customer.subscription.updated`
- [ ] `[M]` Prorrateo: upgrade = días restantes × diferencia prorrateada
- [ ] `[M]` Grace period 7 días: `cron:* * * * *` verifica tenants expirados → soft-lock
- [ ] `[S]` Tests de billing: subscription flow, upgrade, downgrade, cancel

### 3.3 Partners White-Label

- [ ] `[M]` Partners como super-tenants: `partner_id` en `tenants` table, comisión configurable
- [ ] `[M]` Branding custom: logo, colores, dominio, nombre desde `tenants.brand_config`
- [ ] `[M]` Partner dashboard: ven SU precio, NO costos reales SDC
- [ ] `[M]` API de onboarding partner: `POST /api/v1/partners` → create tenant + DNS + deploy
- [ ] `[S]` Tests de partner: pricing oculto, branding, aislamiento

### 3.4 Multi-tenant Infra

- [ ] `[M]` Qdrant: collection por tenant, creada automáticamente al crear tenant
- [ ] `[M]` Neo4j: database por tenant (Enterprise) o `tenant_id` prefix (menor)
- [ ] `[M]` Redis: namespace `tenant:{id}:` en todas las keys
- [ ] `[M]` Resource quotas: Docker resource limits por tenant (CPU, RAM, connections)

---

## Sprint 4: Marketplace + Certificaciones + Gamificación + Analytics + Referidos (Semanas 7-8)

### 4.1 Agent Marketplace

- [ ] `[M]` `capabilities/marketplace/`: registry de agentes publicables, versionado
- [ ] `[M]` API: `GET /marketplace/agents`, `POST /marketplace/agents/:id/install`
- [ ] `[M]` Revenue share: 80% creator, 20% SDC, payout automático mensual
- [ ] `[S]` Tests de marketplace

### 4.2 Certification Pipeline

- [ ] `[M]` Certificación automatizada: security scan, harness compliance, test suite
- [ ] `[S]` Pipeline CI: `make certify` para agentes del marketplace
- [ ] `[M]` Badges de certificación: "Certified", "Trusted", "Enterprise Ready"

### 4.3 Gamificación Multi-Tenant

- [ ] `[M]` `capabilities/gamification/`: XP, niveles, badges con `tenant_id` + `user_id`
- [ ] `[M]` Play to Earn: entrenar agente → XP
- [ ] `[M]` Work to Earn: ventas → bonus
- [ ] `[M]` Learn to Earn: cursos → desbloqueos
- [ ] `[S]` Retos diarios con notificaciones push
- [ ] `[S]` Tests de gamificación

### 4.4 Analytics y Referidos

- [ ] `[M]` `capabilities/analytics/`: eventos con `tenant_id`, dashboard multi-tenant
- [ ] `[M]` Referral system: partners refieren otros partners, comisión recurrente
- [ ] `[M]` Reports semanales: revenue por tenant, usage por capability, agents activos
- [ ] `[S]` Tests de analytics cross-tenant validation

---

## Resumen de esfuerzo

| Sprint | S | M | L | XL | Días estimados |
|--------|---|---|---|----|-----------------|
| Sprint 1 | 5 | 8 | 0 | 0 | 10 |
| Sprint 2 | 3 | 6 | 3 | 0 | 10 |
| Sprint 3 | 3 | 10 | 3 | 0 | 10 |
| Sprint 4 | 4 | 7 | 1 | 0 | 10 |
| **Total** | **15** | **31** | **7** | **0** | **40** |
