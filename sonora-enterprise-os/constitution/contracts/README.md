# Contracts: Constitución
**Spec**: spec.md
---
## API Contracts
- `GET /api/constitution` — Obtener texto constitucional
- `GET /api/principles` — Listar principios rectores
## Data Contracts
```json
{ "constitution": { "id": "string", "version": "string", "principles": ["Principle"] } }
{ "principle": { "id": "string", "name": "string", "description": "string" } }
```
