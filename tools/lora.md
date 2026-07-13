# LoRA Training

- **MCP Server**: lora_mcp
- **Tools**: train_lora, list_loras
- **Input**: artist_name + photos (train), tenant_id (list, optional)
- **Output**: `{weight_id, artist_name, status}` (train), `{lora_models: [...]}` (list)
- **Ejemplo**: `train_lora("Hector Rubio", ["https://...foto1.jpg", ...])`
- **Permisos**: requiere FAL_KEY
- **Endpoint**: POST :8180/mcp/execute
