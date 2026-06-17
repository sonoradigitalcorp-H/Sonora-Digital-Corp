# Contracts: Servidor MCP
**Spec**: spec.md
---
## API Contracts
- `POST /api/mcp/execute` — Ejecutar herramienta MCP
- `GET /api/mcp/tools` — Listar herramientas disponibles
- `GET /api/mcp/status` — Estado del servidor MCP
## Data Contracts
```json
{ "tool_call": { "name": "string", "arguments": "object", "timeout": "int" } }
{ "tool_result": { "status": "success|error", "output": "string", "error": "string|null" } }
```
