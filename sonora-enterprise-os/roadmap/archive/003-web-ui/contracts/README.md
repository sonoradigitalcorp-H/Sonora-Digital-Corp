# Contracts: Web UI
**Spec**: spec.md
---
## API Contracts
- `GET /api/status` — Estado del sistema
- `GET /api/chat/{id}/stream?message=` — SSE chat streaming
- `GET /api/files?path=.` — Explorador de archivos
## Data Contracts
```json
{ "status": { "status": "running", "version": "string", "services": "object" } }
{ "sse_event": { "event": "token|reasoning|tool|done", "data": "object" } }
```
