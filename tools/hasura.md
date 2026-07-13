# Hasura

- **MCP Server**: hasura_mcp
- **Tools**: hasura_query, hasura_mutate, hasura_track_table
- **Input**: query (string), variables (object, optional)
- **Output**: `{data, errors}`
- **Ejemplo**: `hasura_query("{ artists { name } }")`
- **Permisos**: requiere HASURA_ADMIN_SECRET
- **Endpoint**: POST :8180/mcp/execute
