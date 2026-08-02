# Contracts: Mysticverse
**Spec**: spec.md
---
## API Contracts
- `POST /api/mysticverse/twin` — Crear clon digital
- `GET /api/mysticverse/twin/{id}` — Obtener clon
- `POST /api/mysticverse/kyc/age` — Verificar edad
- `POST /api/mysticverse/kyc/identity/{id}` — Verificar identidad
- `POST /api/mysticverse/gamification/xp` — Agregar XP
- `GET /api/mysticverse/gamification/leaderboard` — Leaderboard
## Data Contracts
```json
{ "twin": { "id": "string", "creator_id": "string", "status": "string", "face_trained": "bool" } }
{ "player": { "id": "string", "xp": "int", "level": "int", "badges": ["string"] } }
```
