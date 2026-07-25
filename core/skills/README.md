# core/skills/ — Global Skills Registry

This directory indexes all global (core) skills available to any tenant.

Skills live in two places:
- **Global skills**: `skills/` — available to all tenants (subject to tools.yaml)
- **Tenant skills**: `tenants/<id>/skills/` — exclusive to that tenant

The resolver loads both: global skills first, then tenant-specific overrides.

## How it works

1. The system loads all skills from `skills/` (global)
2. Then loads any skills from `tenants/<id>/skills/` (tenant-specific)
3. If a skill name conflicts, the tenant version wins
4. The orchestrator checks `tools.yaml` before allowing any skill execution
