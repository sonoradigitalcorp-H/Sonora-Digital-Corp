# Contracts: Modularización del Core
**Spec**: spec.md
---
## API Contracts
- `GET /api/modules` — Listar módulos del core
- `GET /api/modules/{name}/deps` — Obtener dependencias de un módulo
## Data Contracts
```json
{ "module": { "name": "string", "path": "string", "lines": "int", "dependencies": ["string"] } }
{ "route": { "method": "GET|POST", "path": "string", "handler": "string", "module": "string" } }
```
