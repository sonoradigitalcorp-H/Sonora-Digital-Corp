# Contracts: Branding y Alma
**Spec**: spec.md
---
## API Contracts
- `GET /api/soul` — Obtener prompt del alma
- `GET /api/brand/voice` — Obtener voz de marca
- `GET /api/bots` — Listar bots de Telegram activos
## Data Contracts
```json
{ "soul": { "version": "string", "tone": "string", "content": "string", "rules": ["string"] } }
{ "bot": { "username": "string", "status": "active|inactive", "last_message": "datetime" } }
```
