# Firecrawl Web Crawler

- **MCP Server**: firecrawl_mcp
- **Tools**: firecrawl_crawl, firecrawl_scrape
- **Input**: url (string)
- **Output**: `{url, content, content_length}`
- **Ejemplo**: `firecrawl_crawl("https://example.com")`
- **Permisos**: requiere FIRECRAWL_API_KEY
- **Endpoint**: POST :8180/mcp/execute
