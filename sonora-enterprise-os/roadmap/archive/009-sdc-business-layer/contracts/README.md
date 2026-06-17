# Contracts: SDC Business Layer
**Spec**: spec.md
---
## API Contracts
- `GET /api/sdc/plans` — Listar planes disponibles
- `GET /api/sdc/plan/{id}` — Obtener detalle de plan
- `POST /api/sdc/onboarding` — Procesar onboarding
- `POST /api/sdc/onboarding/mystic` — Onboarding interactivo Mystic
- `POST /api/payments/create` — Crear pago
- `POST /api/payments/webhook/{provider}` — Webhook de pagos
## Data Contracts
```json
{ "plan": { "id": "string", "name": "string", "price_mxn": "float", "features": ["string"], "limits": "object" } }
{ "onboarding": { "step": "int", "question": "string", "options": ["object"], "completed": "bool" } }
```
