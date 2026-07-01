# ABE Content Factory — System Configuration

**Type**: Agencia Digital
**Tenant**: abe-fenix
**Agents**: abe-content-factory-crm-agent, abe-content-factory-marketing-agent, abe-content-factory-analytics-agent, abe-content-factory-scheduler-agent, abe-content-factory-support-agent
**Features**: client CRM, project tracking, content pipeline, reporting

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
  -d '{"tool":"intake_text","params":{"text":"New agency task","source":"manual"}}'

# Check system health
curl https://sonoradigitalcorp.com/api/health
```

## Dashboards
- https://sonoradigitalcorp.com/dashboard (System)
- https://sonoradigitalcorp.com/adk (Agents)
- https://sonoradigitalcorp.com/abe-services (Services)
- https://sonoradigitalcorp.com/cheatsheet (Reference)
