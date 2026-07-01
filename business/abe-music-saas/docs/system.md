# ABE Music SaaS — System Configuration

**Type**: SaaS Platform
**Tenant**: abe-fenix
**Agents**: abe-music-saas-crm-agent, abe-music-saas-revenue-agent, abe-music-saas-analytics-agent, abe-music-saas-scheduler-agent, abe-music-saas-support-agent
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
