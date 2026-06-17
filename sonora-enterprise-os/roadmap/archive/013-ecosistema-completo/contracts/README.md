# Contracts: Ecosistema Completo
**Spec**: spec.md
---
## API Contracts
- `GET /api/skills` — Listar todas las skills del ecosistema
- `GET /api/unified/status` — Estado de plataformas
- `GET /api/webhook/n8n-status` — Estado de n8n
## Data Contracts
```json
{ "skill": { "name": "string", "description": "string", "source": "openclaw|jarvis|hermes", "enabled": "bool" } }
{ "platform": { "name": "string", "state": "connected|disconnected", "last_seen": "datetime" } }
```
