# Engram Memory

- **MCP Server**: engram_mcp
- **Tools**: engram_save, engram_get, engram_search, engram_list_layers
- **Input**: tenant_id, key, value/user_id/query, layer/limit/tags (opcional)
- **Output**: `{saved: true, id}` o `{found: true, value}` o `{results: [...]}`
- **Ejemplo**: `engram_save("abe-music", "user_pref", "dark", "user_1")`
- **Permisos**: requiere tenant_id (aislado por tenant)
- **Endpoint**: POST :8180/mcp/execute
