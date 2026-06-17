# Data Model: Servidor MCP
**Spec**: spec.md
---
## Entidades
| Entidad | Atributos | Descripción |
|---------|-----------|-------------|
| MCPTool | name, description, parameters, returns | Herramienta expuesta vía MCP |
| MCPServer | id, port, status, type | Servidor MCP (local/remote) |
| ToolCall | id, tool_name, arguments, result, timestamp | Invocación de herramienta |
## Relaciones
```
(MCPServer)-[:EXPOSES]->(MCPTool)
(ToolCall)-[:USES]->(MCPTool)
```
