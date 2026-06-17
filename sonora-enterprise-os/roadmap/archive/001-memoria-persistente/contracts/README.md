# Contracts: Memoria Persistente
**Spec**: spec.md
---
## API Contracts
- `POST /api/sessions` — Crear sesión
- `GET /api/sessions/{id}` — Obtener sesión con mensajes
- `POST /api/sessions/{id}/messages` — Agregar mensaje
- `DELETE /api/sessions/{id}` — Eliminar sesión
## Data Contracts
```json
{ "session": { "id": "string", "title": "string", "messages": ["Message"], "created_at": "datetime" } }
{ "message": { "role": "user|assistant|system", "content": "string", "tokens": "int" } }
```
