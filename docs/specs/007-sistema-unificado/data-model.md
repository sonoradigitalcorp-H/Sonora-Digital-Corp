# Data Model: Sistema Unificado
**Spec**: spec.md
---
## Entidades
| Entidad | Atributos | Descripción |
|---------|-----------|-------------|
| UnifiedAgent | name, bridge_type, health_status | Agente con bridge a externo |
| ApprovalTicket | id, action, status, created_at | Solicitud de aprobación humana |
| BridgeMessage | id, channel, direction, content, status | Mensaje multi-canal |
## Relaciones
```
(UnifiedAgent)-[:REQUIRES]->(ApprovalTicket)
(BridgeMessage)-[:SENT_VIA]->(UnifiedAgent)
```
