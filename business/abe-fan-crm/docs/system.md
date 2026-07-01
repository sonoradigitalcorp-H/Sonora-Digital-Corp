# ABE Fan CRM — System Configuration

**Type**: E-commerce
**Tenant**: abe-fenix
**Agents**: abe-fan-crm-crm-agent, abe-fan-crm-marketing-agent, abe-fan-crm-analytics-agent, abe-fan-crm-scheduler-agent
**Features**: product management, order tracking, customer CRM, marketing campaigns

## Architecture
- Gateway: MCP :18989
- Auth: JWT RS256
- Models: 4x llama3.2:3b (Ollama, local, 0$/call)
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
  -d '{"tool":"intake_text","params":{"text":"New ecommerce task","source":"manual"}}'

# Check system health
curl https://sonoradigitalcorp.com/api/health
```

## Dashboards
- https://sonoradigitalcorp.com/dashboard (System)
- https://sonoradigitalcorp.com/adk (Agents)
- https://sonoradigitalcorp.com/abe-services (Services)
- https://sonoradigitalcorp.com/cheatsheet (Reference)
