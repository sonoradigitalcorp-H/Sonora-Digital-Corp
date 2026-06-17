# Contracts: Sistema Unificado
**Spec**: spec.md
---
## API Contracts
- `GET /api/unified/status` — Estado de todos los bridges
- `GET /api/approvals` — Listar aprobaciones pendientes
- `POST /api/approvals/{id}/approve` — Aprobar acción
- `POST /api/approvals/{id}/reject` — Rechazar acción
## Data Contracts
```json
{ "unified_status": { "hermes": "ok|offline", "openclaw": "ok|offline", "gbrain": "ok|offline" } }
{ "approval": { "ticket": "string", "action": "string", "status": "pending|approved|rejected", "created_at": "datetime" } }
```
