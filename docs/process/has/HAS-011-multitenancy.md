# HAS-011 — Hermes Architecture Standard: Multi-tenancy

**Status:** Draft v1
**Domain:** infrastructure
**Updated:** 2026-07-08
**Depends on:** HAS-000, HAS-001

---

## 1. Purpose

Define the multi-tenancy model. From day one, every table, event, and memory includes a `tenant_id`. The system starts with one tenant (ABE Music) but supports adding new tenants without migration.

---

## 2. Tenant Model

```
tenant_id (UUID) ──── isolation level ──── configuration
     │                                        │
     ├── ABE Music                             ├── constitution overrides
     ├── Sonora CRM        (future)            ├── capability allowlist
     └── Sonora Analytics  (future)            └── cost budget
```

## 3. Isolation Levels

| Level | Description | When to use |
|---|---|---|
| **Column** | `tenant_id` column in every table | Default — all tenants share infrastructure |
| **Schema** | Separate DB schema per tenant | Sensitive data, compliance requirements |
| **Database** | Separate DB instance per tenant | High-security tenants, different regions |

## 4. Implementation

```python
@dataclass
class Tenant:
    id: str
    name: str
    isolation: str              # column | schema | database
    capabilities: list[str]    # Allowed capabilities
    constitution_overrides: dict  # Override specific constitution rules
    budget: float               # Monthly cost budget
```

Every database query includes `WHERE tenant_id = ?`. Every event includes `tenant` field (HAS-003). Every memory store accepts tenant_id.

## 5. Events

| Event | Trigger | Payload |
|---|---|---|
| `tenant.created` | New tenant provisioned | `{ id, name, isolation }` |
| `tenant.config.updated` | Tenant configuration changed | `{ id, changes }` |
| `tenant.budget.exceeded` | Tenant exceeded budget | `{ id, budget, actual }` |
