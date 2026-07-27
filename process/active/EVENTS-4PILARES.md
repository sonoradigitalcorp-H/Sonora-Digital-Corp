# Events — 4 Pilares Multi-Tenant

## Registro de Eventos

| Evento | Trigger | Datos | Destino |
|--------|---------|-------|---------|
| `tenant.created` | POST /api/v1/tenants | `{tenant_id, name, plan, domain, created_at}` | events.jsonl, analytics |
| `tenant.activated` | Stripe webhook: payment confirmed | `{tenant_id, plan, stripe_sub_id}` | events.jsonl, billing |
| `tenant.suspended` | Grace period expired (cron) | `{tenant_id, days_overdue}` | events.jsonl, email queue |
| `tenant.upgraded` | POST /api/v1/tenants/:id/upgrade | `{tenant_id, old_plan, new_plan, prorated_amount}` | events.jsonl, billing |
| `tenant.downgraded` | POST /api/v1/tenants/:id/downgrade | `{tenant_id, old_plan, new_plan, effective_date}` | events.jsonl, billing |
| `tenant.cancelled` | DELETE /api/v1/tenants/:id | `{tenant_id, reason, days_active}` | events.jsonl, data_export |
| `tenant.export.requested` | POST /api/v1/tenants/:id/export | `{tenant_id, format, requested_at}` | async job queue |
| `tenant.export.completed` | Export job finished | `{tenant_id, download_url, expires_at}` | email, events.jsonl |
| `partner.created` | POST /api/v1/partners | `{partner_id, name, commission_pct, domain}` | events.jsonl |
| `agent.published` | Agent passes certification | `{agent_id, name, creator_id, version}` | marketplace, events.jsonl |
| `agent.installed` | Tenant installs from marketplace | `{agent_id, tenant_id, revenue_share}` | marketplace, billing |
| `capability.rate_limited` | Tenant exceeds quota | `{tenant_id, capability, current_usage, limit}` | alerts, events.jsonl |
| `tenant.rls_violation` | Cross-tenant access attempt detected | `{tenant_id, attempted_resource, blocked}` | security alerts, events.jsonl |

## Storage

Todos los eventos se persisten en:
1. `state/events/events.jsonl` (append-only log local)
2. `capabilities/analytics/` (eventos estructurados por tenant_id)
3. Postgres en tabla `events` (para queries analíticas)
