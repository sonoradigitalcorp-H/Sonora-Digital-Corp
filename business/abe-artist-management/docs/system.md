# ABE Artist Management — System Configuration

**Type**: Sello Discográfico
**Tenant**: abe-fenix
**Agents**: abe-artist-management-crm-agent, abe-artist-management-revenue-agent, abe-artist-management-marketing-agent, abe-artist-management-analytics-agent, abe-artist-management-scheduler-agent
**Features**: artist management, revenue tracking, content generation, analytics

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
  -d '{"tool":"intake_text","params":{"text":"New music_label task","source":"manual"}}'

# Check system health
curl https://sonoradigitalcorp.com/api/health
```

## Dashboards
- https://sonoradigitalcorp.com/dashboard (System)
- https://sonoradigitalcorp.com/adk (Agents)
- https://sonoradigitalcorp.com/abe-services (Services)
- https://sonoradigitalcorp.com/cheatsheet (Reference)
