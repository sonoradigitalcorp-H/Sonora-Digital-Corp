# Open Lovable — App Generator

- **MCP Server**: openlovable_mcp
- **Tools**: lovable_generate_page, lovable_clone_site, lovable_extract_brand, lovable_edit_page
- **Input**: prompt (generate), url (clone), prompt+current_code (edit)
- **Output**: `{content: "...", files: [...]}`
- **Ejemplo**: `lovable_generate_page("Create a dashboard for ABE Music with artist list")`
- **Permisos**: requiere OPENROUTER_API_KEY
- **Endpoint**: POST :8180/mcp/execute
