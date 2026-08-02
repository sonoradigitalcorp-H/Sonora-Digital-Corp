# Contracts: ABE MUSIC
**Spec**: spec.md
---
## API Contracts
- `POST /api/abe/artists` — Crear artista
- `GET /api/abe/artists` — Listar artistas
- `GET /api/abe/artists/{id}` — Obtener artista
- `POST /api/abe/artists/{id}/releases` — Crear lanzamiento
- `GET /api/abe/dashboard/ceo` — Dashboard del CEO
## Data Contracts
```json
{ "artist": { "id": "string", "nombre": "string", "streams": "int", "revenue": "float", "status": "string" } }
{ "release": { "id": "string", "titulo": "string", "streams": "int", "revenue": "float" } }
{ "ceo_dashboard": { "total_artists": "int", "total_revenue": "float", "top_artists": ["Artist"], "revenue_by_source": "object" } }
```
