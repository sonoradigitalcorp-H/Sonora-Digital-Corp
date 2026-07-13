# RAG — Qdrant Knowledge Base

- **MCP Server**: rag_mcp
- **Tools**: rag_search, rag_index, rag_list_collections
- **Input**: tenant_id, query (search), document_id+content (index)
- **Output**: `{results: [{payload, score}]}` o `{indexed: true}`
- **Ejemplo**: `rag_search("abe_music", "¿qué productos tiene Hector?")`
- **Permisos**: requiere tenant_id (aislado por tenant)
- **Endpoint**: POST :8180/mcp/execute
