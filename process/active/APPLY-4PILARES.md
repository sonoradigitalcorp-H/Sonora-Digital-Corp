# Apply Instructions — Transformación 4 Pilares Multi-Tenant

Para: **Builder Agent**
Desde: **SDD Orchestrator**
Basado en: `SPEC-20260726-4PILARES`, `plan-4PILARES.md`, `tasks-4PILARES.md`

---

## Regla de Oro

**NO rompas nada existente.** Cada sprint debe mantener compatibilidad hacia atrás. Los productos actuales deben seguir funcionando mientras se migran.

---

## Sprint 1: Products + Capabilities (orden de ejecución)

### Paso 1: Crear estructura de directorios

```
products/       → ya existe, añadir ProductBase class
capabilities/   → NUEVO
  auth/
  memory/
  ai/
  voice/
  channels/
    whatsapp/
    telegram/
    web/
    voice/
  payments/
  analytics/
  tenants/      → preparado para Sprint 3
  marketplace/  → preparado para Sprint 4
  gamification/ → preparado para Sprint 4
agents/         → NUEVO
  sdk/
  registry.yaml
  sales/
  support/
  receptionist/
  orchestrator/
  accounting/
  marketing/
infra/          → ya existe, mover bajo 4-pillars
```

### Paso 2: ProductBase class

Crear `products/__init__.py`:

```python
from dataclasses import dataclass, field
from typing import Protocol

class Capability(Protocol):
    def execute(self, tenant_id: str, **kwargs) -> dict: ...

@dataclass(frozen=True)
class ProductBase:
    id: str
    name: str
    version: str = "1.0.0"
    required_capabilities: list[str] = field(default_factory=list)
    tenant_id: str = ""

    def execute(self, capability: Capability, **kwargs) -> dict:
        return capability.execute(self.tenant_id, **kwargs)
```

### Paso 3: Capabilities wrapper (no mover código aún)

- Cada capability envuelve el código existente de `apps/` sin moverlo:
  ```python
  # capabilities/auth/__init__.py
  def get_auth_capability() -> AuthCapability:
      from apps.core.auth import verify_token  # import temporal
      ...
  ```
- En Sprint 3 se mueve el código definitivamente (después de que todo funcione)

### Paso 4: Products refactor

- Cada producto en `products/` debe importar de `capabilities/` en lugar de `apps/`:
  ```python
  # ANTES:
  from apps.core.ai import ask_llm
  # DESPUÉS:
  from capabilities.ai import AIcapability
  ai = AIcapability(tenant_id="sdc")
  ai.ask(prompt=...)
  ```
- Verificar que `make test` sigue pasando después de cada migración

### Paso 5: Tests de capabilities

Cada capability debe tener tests que verifiquen:
- `test_{capability}_happy_path`: funciona con tenant_id correcto
- `test_{capability}_without_tenant`: falla con 403
- `test_{capability}_rate_limit`: respeta cuota del plan

---

## Sprint 2: Agents (orden de ejecución)

### Paso 1: Agent Harness SDK

`agents/sdk/harness.py`:

```python
@dataclass(frozen=True)
class AgentHarness:
    mission: str
    capabilities: list[str]
    skills: list[str]
    policies: list[str]
    memory_scope: str  # "working" | "task" | "project" | "customer" | "business"
    events: list[str]  # eventos que emite este agente
    failure_modes: list[str]
    recovery_procedures: list[str]
    metrics: list[str]
```

### Paso 2: Agent Registry

`agents/registry.yaml`:
```yaml
agents:
  - id: sales
    name: Sales Agent
    harness: agents/sales/harness.yaml
    capabilities: [auth, ai, memory, channels.whatsapp, channels.web]
    events: [lead.received, lead.qualified, proposal.generated, deal.won, deal.lost]
  - id: support
    name: Support Agent
    harness: agents/support/harness.yaml
    capabilities: [auth, ai, memory, channels.all]
    events: [ticket.created, ticket.resolved, ticket.escalated]
  ...
```

### Paso 3: Orchestrator

```python
# agents/orchestrator/engine.py
class Orchestrator:
    def route_event(self, event: dict, tenant_id: str):
        agent_id = self.policy_engine.match(event, tenant_id)
        agent = self.agent_registry.get(agent_id)
        return agent.execute(event, tenant_id)
```

### Paso 4: Workflows

```yaml
# workflows/lead-to-cash.yaml
steps:
  - agent: sales
    event: lead.received
  - agent: sales
    event: lead.qualified → proposal.generated
  - agent: accounting
    event: deal.won → invoice.created
  - agent: support
    event: customer.onboarded → ticket.pending
```

---

## Sprint 3: Tenants + Billing (orden de ejecución)

### Paso 1: Base de datos

```sql
-- migrations/001_create_tenants.sql
CREATE TABLE tenants (
  tenant_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  plan TEXT NOT NULL CHECK (plan IN ('starter','pro','business','enterprise')),
  status TEXT NOT NULL DEFAULT 'trial' CHECK (status IN ('trial','active','suspended','cancelled')),
  custom_domain TEXT UNIQUE,
  brand_config JSONB DEFAULT '{}',
  features JSONB DEFAULT '{}',
  stripe_customer_id TEXT,
  stripe_subscription_id TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  trial_ends_at TIMESTAMPTZ DEFAULT now() + interval '7 days'
);

ALTER TABLE clients ADD COLUMN tenant_id UUID REFERENCES tenants(tenant_id);
ALTER TABLE invoices ADD COLUMN tenant_id UUID REFERENCES tenants(tenant_id);
ALTER TABLE events ADD COLUMN tenant_id UUID REFERENCES tenants(tenant_id);
-- ... etc para todas las tablas existentes

-- RLS
ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
CREATE POLICY clients_isolation ON clients
  USING (tenant_id = current_setting('app.tenant_id')::UUID);
```

### Paso 2: Middleware multi-tenant

```python
# capabilities/auth/middleware.py
async def tenant_middleware(request: Request, call_next):
    token = request.headers.get("Authorization")
    tenant_id = extract_tenant_from_token(token)
    if not tenant_id:
        return JSONResponse(status_code=403, content={"error": "no_tenant"})
    
    # Set tenant context for RLS
    await database.execute(
        f"SELECT set_config('app.tenant_id', '{tenant_id}', false)"
    )
    
    # Set tenant context for Redis
    request.state.tenant_id = tenant_id
    request.state.redis_prefix = f"tenant:{tenant_id}:"
    
    response = await call_next(request)
    return response
```

### Paso 3: Plans config

```yaml
# config/plans.yaml
plans:
  starter:
    price_monthly: 49
    agents: 1
    interactions_monthly: 1000
    clients: 10
    channels: [web]
    storage_gb: 1
    features: [basic_analytics]
  pro:
    price_monthly: 149
    agents: 3
    interactions_monthly: 10000
    clients: 50
    channels: [web, whatsapp, telegram]
    storage_gb: 10
    features: [basic_analytics, exports, custom_branding]
  business:
    price_monthly: 499
    agents: 10
    interactions_monthly: 100000
    clients: 500
    channels: [all]
    storage_gb: 100
    features: [all, api_access, priority_support]
  enterprise:
    price_monthly: 999
    agents: unlimited
    interactions_monthly: unlimited
    clients: unlimited
    channels: [all]
    storage_gb: 1000
    features: [all, dedicated_db, sla, white_label, custom_terms]
```

### Paso 4: Stripe Connect

```python
# capabilities/payments/stripe_connect.py
# Webhooks a implementar:
# - checkout.session.completed → tenant.created + tenant.activated
# - invoice.paid → tenant.status = active
# - invoice.payment_failed → tenant.status = past_due, email warning
# - customer.subscription.updated → tenant.upgraded | tenant.downgraded
# - customer.subscription.deleted → tenant.cancelled + export
```

---

## Verificación de no-rotura

Después de CADA paso, ejecutar:

```bash
cd ~/sdc && make test        # 852+ tests deben seguir pasando
cd ~/sdc && make eval        # structural tests
cd ~/sdc && make lint        # ruff sin errores nuevos
```

Si un test falla:
1. NO sigas al siguiente paso
2. Arregla el test o el código
3. Vuelve a correr `make test`
4. Solo entonces continúa

---

## Archivos a crear (orden)

```
1.  capabilities/__init__.py
2.  capabilities/auth/__init__.py
3.  capabilities/memory/__init__.py
4.  capabilities/ai/__init__.py
5.  capabilities/voice/__init__.py
6.  capabilities/channels/__init__.py
7.  capabilities/channels/whatsapp.py
8.  capabilities/channels/telegram.py
9.  capabilities/channels/web.py
10. capabilities/channels/voice.py
11. capabilities/payments/__init__.py
12. capabilities/analytics/__init__.py
13. capabilities/tenants/__init__.py       (Sprint 3)
14. capabilities/marketplace/__init__.py  (Sprint 4)
15. capabilities/gamification/__init__.py (Sprint 4)
16. agents/sdk/harness.py
17. agents/registry.yaml
18. agents/sales/harness.yaml
19. agents/support/harness.yaml
20. agents/receptionist/harness.yaml
21. agents/orchestrator/engine.py
22. products/__init__.py  (actualizar)
23. config/plans.yaml     (nuevo)
24. infra/migrations/001_create_tenants.sql
```

## Archivos a mover/renombrar (Sprint 3, después de verificar)

```
apps/core/ai.py          → capabilities/ai/provider.py
apps/core/memory.py      → capabilities/memory/engram.py
apps/core/jwt.py         → capabilities/auth/jwt.py
apps/hermes/gateway.py   → capabilities/channels/hermes.py
apps/twilio-voice/       → capabilities/voice/twilio.py
products/manager.py      → capabilities/tenants/product_registry.py
infra/fleet.yml          → infra/fleet/fleet.yml  (si aplica)
```

NO mover nada en Sprint 1 o 2. Solo envolver con capabilities wrappers.

---

## Qué NO hacer

- ❌ No mover archivos de `apps/` a `capabilities/` hasta Sprint 3
- ❌ No cambiar imports de productos existentes hasta que el wrapper capability esté probado
- ❌ No borrar código de `apps/` aunque parezca duplicado (mantener compatibilidad hacia atrás)
- ❌ No deployar RLS en producción hasta tener tests de integración cross-tenant
- ❌ No exponer APIs de tenant sin auth middleware
- ❌ No compartir colecciones de Qdrant entre tenants
