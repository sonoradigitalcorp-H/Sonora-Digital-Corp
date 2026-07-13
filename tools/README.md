# Tool Registry

Cada herramienta MCP tiene su propia documentación en este directorio.

## Cómo agregar una nueva tool

1. Crear el MCP server en `core/mcp/servers/{name}_mcp.py`
2. Agregar `tools/{name}.md` con la documentación
3. Ejecutar `scripts/generate-tool-registry.py` para actualizar `registry.json`

## Formato de cada doc

```markdown
# {Nombre}
- **MCP Server**: {server_name}
- **Tools**: {tool1}, {tool2}, ...
- **Input**: descripción de los parámetros
- **Output**: descripción de la respuesta
- **Ejemplo**: curl :8180/mcp/execute -d '{...}'
- **Permisos**: qué se necesita para usarla
- **Endpoint**: POST /mcp/execute
```

## Tools disponibles

Ver `registry.json` para la lista completa y actualizada.
