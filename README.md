# Native Agent OS

MCP-native agent operating system.  
155 tools · 6 agents · 6 workflows · 6 local models · 1 gateway.

```
curl https://sonoradigitalcorp.com/api/health
```

## Architecture

```
Request → MCP Gateway (:18989) → CapabilityRegistry → Tools/Agents/Workflows
```

| Component | What |
|-----------|------|
| Gateway | MCP Protocol, JWT RS256 auth, rate limiting |
| CapabilityRegistry | Routes tasks by capability to the right agent |
| ADK | Declarative agents defined in YAML |
| Workflow Engine | Multi-step, multi-agent graph execution |
| Swarm Engine | Parallel agent coordination |
| Provider Router | 6 Ollama models + OpenRouter + OpenCodeGo |

## Quick Start

```bash
curl -X POST https://sonoradigitalcorp.com/api/auth/token \
  -d '{"client_id":"sdc-core","client_secret":"sdc_secret_ent3rpr1s3_k3y_2026"}'

curl https://sonoradigitalcorp.com/api/tools \
  -H "Authorization: Bearer <token>"
```

## Dashboards

```
/dashboard       → System status
/adk             → Agent management
/workflow-editor → Visual workflows
/tenant          → Tenant panel
/cheatsheet      → Quick reference
```

## Stats

```
155 MCP tools · 6 ADK agents · 6 workflows · 6 Ollama models
3 providers · 16 capabilities · 128 skills · 5 plugins
535 tests · 0 failures · Score 84/100
```

## License

MIT
