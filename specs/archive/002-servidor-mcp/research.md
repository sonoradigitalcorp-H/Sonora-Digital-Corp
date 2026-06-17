# Research: Servidor MCP
**Spec**: spec.md
---
## Tecnologías Evaluadas
| Opción | Ventajas | Desventajas | Decisión |
|--------|----------|-------------|----------|
| FastMCP | Nativo Python, SSE, JSON-RPC | Relativamente nuevo | ✅ Seleccionado |
| Docker + MCP | Aislamiento, portable | Overhead de red | ✅ usado para despliegue |
## Decisión Arquitectónica
- **Selección**: FastMCP server dockerizado + MCP connectors para HF y GitHub
- **Motivo**: Skills modulares, reemplazables sin tocar código core
## Limitaciones
1. MCP requiere servidor corriendo para funcionar
2. Sin autenticación entre MCP y JARVIS
