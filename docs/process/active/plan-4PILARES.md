# Plan — Transformación 4 Pilares Multi-Tenant

## Resumen

4 sprints × 2 semanas = 8 semanas total.

| Sprint | Foco | Depende de |
|--------|------|------------|
| **Sprint 1** | Products + Capabilities funcionales | N/A |
| **Sprint 2** | Agents + Orchestrator + Flujos | Sprint 1 |
| **Sprint 3** | Tenants + Branding + Plans + Billing + Partners | Sprint 1+2 |
| **Sprint 4** | Marketplace + Certificaciones + Gamificación + Analytics + Referidos | Sprint 3 |

### Timeline visual

```
Semana 1-2  │ Sprint 1: Products + Capabilities
            │   ┌─────────────────────────────┐
            │   │ Estructura 4 pilares        │
            │   │ Capabilities core (auth,    │
            │   │ memory, AI, channels)       │
            │   │ Products refactor           │
            │   └─────────────────────────────┘
Semana 3-4  │ Sprint 2: Agents + Orchestrator
            │   ┌─────────────────────────────┐
            │   │ Agent Harness SDK           │
            │   │ 5 agents canónicos          │
            │   │ Orchestrator engine         │
            │   │ Event-driven flows          │
            │   └─────────────────────────────┘
Semana 5-6  │ Sprint 3: Tenants + Billing
            │   ┌─────────────────────────────┐
            │   │ Tenant Registry + RLS       │
            │   │ Multi-tenant infra          │
            │   │ Plans + Stripe billing      │
            │   │ Partners white-label        │
            │   └─────────────────────────────┘
Semana 7-8  │ Sprint 4: Marketplace + Growth
            │   ┌─────────────────────────────┐
            │   │ Agent marketplace           │
            │   │ Certification pipeline      │
            │   │ Gamification multi-tenant   │
            │   │ Analytics + Referidos       │
            │   └─────────────────────────────┘
```

### Dependencias críticas

```
Sprint 1 ──► Sprint 2 ──► Sprint 3 ──► Sprint 4
                │                          │
                └── capabilities API ──────┘
                     (necesaria en todos)
```
