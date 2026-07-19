# skills/creator — Agent-Native Company Builder

**Inherits**: OMEGA PROMPT v10.0 + SOUL.md
**Template Version**: 1.0.0
**Audit ID**: SKILL-CRT-001

---

## 1. Business Objective

Build complete agent-native companies in hours — each with a smart app, 6 specialized agents, tenant database, knowledge base, voice cloning, and custom model training — deployable at {name}.sonoracorp.com.

## 2. Inputs (Gherkin)

```gherkin
Given a company blueprint exists (name, template, contact info)
And the tenant has provided assets (photos, audio, brand guidelines)
When the creator pipeline is triggered with the blueprint
```

## 3. Outputs (Gherkin)

```gherkin
Then a React/Vite app is generated via Lovable
And a Hasura tenant is created with RLS policies
And 6 agent definitions are created in agents/{tenant}/
And optional LoRA model training completes (if photos exist)
And optional voice cloning completes (if audio exists)
And nginx + systemd service is configured and verified
```

## 4. Events

```
Events:
- agent:manifest_created: a new company manifest was registered
- agent:agent_spawned: a new agent was spawned for a tenant
- creator:company:deployed: full company deployment completed
- creator:company:failed: deployment encountered an unrecoverable error
```

## 5. Dependencies

```
Dependencies:
- Open Lovable: service — page/app generation
- Hasura: service — tenant and RLS setup
- Qdrant: service — knowledge base per tenant
- FAL AI: service — LoRA model training
- OmniVoice: service — voice cloning
- Nginx: service — reverse proxy configuration
- Engram: service — tenant registry
```

## 6. Tools

```
Tools:
- lovable_generate_page: generate React/Vite app from blueprint
- hasura_query: check existing tenants and data
- hasura_mutate: create tenant schema and RLS policies
- engram_save: register tenant in persistent memory
- upload_file: deploy static assets
```

## 7. Policies

```
Policies:
- Each tenant must have a unique name (enforced by Hasura)
- All generated apps must pass accessibility checks
- Voice cloning requires explicit consent documentation
- LoRA training must not exceed 30 minutes per model
- Deployments must verify HTTP 200 before marking complete
- Tenant data must be fully isolated via RLS
```

## 8. Success Metrics

```gherkin
Success Metrics:
- build_time: Given blueprint When deployed Then total hours
  Target: < 4 hours
- agent_count: Given tenant created When spawned Then number of agents
  Target: 6 agents
- uptime: Given deployed When monitored Then 30-day availability
  Target: > 99.9%
```

## 9. Failure Conditions

```
Failure Conditions:
- Lovable generation fails: page template error (detect via HTTP response)
- Hasura mutation timeout: schema creation hangs (detect via 30s timeout)
- LoRA training OOM: model exceeds GPU memory (detect via process exit)
- Voice clone quality low: similarity score below threshold (detect via metric)
- DNS propagation delay: {name}.sonoracorp.com unreachable (detect via curl)
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. Retry Lovable generation once with simplified blueprint
2. If Hasura fails → check schema exists, re-run mutation with reset
3. If LoRA OOM → reduce training steps, retry with smaller model
4. If voice clone fails → proceed without voice, flag for manual review
5. If DNS fails → wait 60s, retry verification up to 5x
6. Log full deployment to state/logs/skills/creator.log
```

## 11. Business Value

```
Business Value: Builds complete agent-native companies in hours. Estimated $5k/sale.
```

## 12. Parent OS

```
Parent OS: Agent
```

## 13. Version

```
Version: 1.0.0
```

## 14. Audit Trail

```
Audit Trail:
- ADR: ADR-2026-CRT-001
- Events: agent:manifest_created, agent:agent_spawned, creator:company:deployed, creator:company:failed
- Logs: state/logs/skills/creator.log
```
