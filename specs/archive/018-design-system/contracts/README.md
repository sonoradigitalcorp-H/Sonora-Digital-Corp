# Contracts: Design System

**Spec**: spec.md

## API Contracts
- `GET /api/design-tokens` — Obtener tokens de diseño
- `GET /api/components` — Listar componentes disponibles
- `POST /api/components` — Registrar nuevo componente

## Data Contracts
```json
{ "design-token": { "name": "string", "value": "string", "category": "color|spacing|typography" } }
{ "component": { "name": "string", "styles": "object", "variants": ["string"] } }
```
