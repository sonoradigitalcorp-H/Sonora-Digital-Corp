# Content Video Generation

- **MCP Server**: content_mcp
- **Tools**: generate_video
- **Input**: artist_name + prompt (requerido), lora_weight_id + script_text + content_type (opcional)
- **Output**: `{video_url, artist, model_used}` o `{fallback: true, message}`
- **Ejemplo**: `generate_video("Hector Rubio", "Hector saluda a sus fans", "lora_abc123", "...script...", "clase")`
- **Permisos**: requiere FAL_KEY
- **Endpoint**: POST :8180/mcp/execute
