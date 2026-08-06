# Playwright Browser

- **MCP Server**: playwright_mcp
- **Tools**: browser_navigate, browser_screenshot, browser_extract
- **Input**: url (navigate), selector+url (extract)
- **Output**: `{content, title, url}` o `{screenshot_url}`
- **Ejemplo**: `browser_navigate("https://example.com")`
- **Permisos**: acceso a internet
- **Endpoint**: POST :8180/mcp/execute
