# LLM Chat

- **MCP Server**: llm_mcp
- **Tools**: llm_chat, llm_complete
- **Input**: system+message (chat), prompt (complete)
- **Output**: `{content, model, usage}`
- **Ejemplo**: `llm_chat("You are an assistant", "¿Qué es ABE Music?")`
- **Permisos**: requiere OPENROUTER_API_KEY
- **Endpoint**: POST :8180/mcp/execute
