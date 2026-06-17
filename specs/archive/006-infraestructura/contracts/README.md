# Contracts: Infraestructura
**Spec**: spec.md
---
## API Contracts
- `GET /api/health` — Health check general
- `POST /api/backup` — Ejecutar backup manual
- `GET /api/logs?service=&level=&since=` — Obtener logs
## Data Contracts
```json
{ "health": { "status": "healthy|unhealthy", "services": {"name": "up|down"} } }
{ "backup": { "id": "string", "path": "string", "size": "int", "timestamp": "datetime" } }
```
