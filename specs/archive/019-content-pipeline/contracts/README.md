# Contracts: Content Pipeline

**Spec**: spec.md

## API Contracts
- `POST /api/content/generate` — Generar contenido
- `POST /api/content/deliver` — Entregar contenido
- `GET /api/content/templates` — Listar plantillas
- `POST /api/pipeline/trigger` — Ejecutar pipeline

## Data Contracts
```json
{ "generate": { "template": "string", "topic": "string", "formats": ["video","audio","article"] } }
{ "deliver": { "content_id": "string", "channels": ["email","telegram","web"] } }
```
