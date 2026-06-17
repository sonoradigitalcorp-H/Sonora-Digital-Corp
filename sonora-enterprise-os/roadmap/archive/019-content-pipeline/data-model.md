# Data Model: Content Pipeline

**Spec**: spec.md

## Entidades
| Entidad | Atributos | Descripción |
|---------|-----------|-------------|
| Content | id, type, title, format, url, created_at | Pieza de contenido generado |
| Pipeline | id, name, schedule, last_run, status | Pipeline de contenido diario |
| Delivery | id, content_id, channel, status, delivered_at | Entrega a canal específico |
| Template | id, name, format, prompt, style | Plantilla de contenido |

## Relaciones
```
(Pipeline)-[:GENERATES]->(Content)
(Content)-[:DELIVERED_VIA]->(Delivery)
(Content)-[:USES_TEMPLATE]->(Template)
```
