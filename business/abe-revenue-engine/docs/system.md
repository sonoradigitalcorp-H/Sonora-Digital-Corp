# ABE Revenue Engine — System Configuration

**Type**: SaaS Platform
**Tenant**: abe-fenix
**Agents**: abe-revenue-engine-crm-agent, abe-revenue-engine-revenue-agent, abe-revenue-engine-analytics-agent, abe-revenue-engine-scheduler-agent, abe-revenue-engine-support-agent
**Features**: user management, billing, analytics, support tickets

## Architecture
- Gateway: MCP :18989
- Auth: JWT RS256
- Models: 5x llama3.2:3b (Ollama, local, 0$/call)
- Fallback: opencode-go

## Quick Start
```bash
# List agents
curl -X POST https://sonoradigitalcorp.com/api/call \
  -H "Authorization: Bearer <token>" \
  -d '{"tool":"adk_list_agents","params":{}}'

# Run business tasks
curl -X POST https://sonoradigitalcorp.com/api/call \
  -H "Authorization: Bearer <token>" \
  -d '{"tool":"intake_text","params":{"text":"New saas task","source":"manual"}}'

# Check system health
curl https://sonoradigitalcorp.com/api/health
```

## Dashboards
- https://sonoradigitalcorp.com/dashboard (System)
- https://sonoradigitalcorp.com/adk (Agents)
- https://sonoradigitalcorp.com/abe-services (Services)
- https://sonoradigitalcorp.com/cheatsheet (Reference)
