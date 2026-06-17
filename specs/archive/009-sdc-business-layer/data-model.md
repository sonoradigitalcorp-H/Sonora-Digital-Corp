# Data Model: SDC Business Layer
**Spec**: spec.md
---
## Entidades
| Entidad | Atributos | Descripción |
|---------|-----------|-------------|
| Customer | id, nombre, email, telefono, tipo, nicho, plan, status | Cliente de SDC |
| Subscription | id, plan, precio, multiplicador, stripe_id, start, end, status | Suscripción activa |
| Transaction | id, plan, amount, provider, status, created_at | Pago registrado |
| Plan | id, name, price, features, limits, type | Plan de suscripción |
## Relaciones
```
(Customer)-[:TIENE_SUSCRIPCION]->(Subscription)
(Customer)-[:REALIZO]->(Transaction)
(Subscription)-[:OF_PLAN]->(Plan)
```
