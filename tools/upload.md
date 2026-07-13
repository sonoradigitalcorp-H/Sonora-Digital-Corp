# File Upload

- **MCP Server**: upload_mcp
- **Tools**: upload_file, get_file_url, list_files, delete_file
- **Input**: bucket, path, content_b64 (base64), content_type
- **Output**: `{url, path, bucket}` o `[{...}]`
- **Ejemplo**: `upload_file("sdc-assets", "abe/foto.jpg", "...b64...", "image/jpeg")`
- **Permisos**: requiere SUPABASE_SERVICE_KEY
- **Endpoint**: POST :8180/mcp/execute
