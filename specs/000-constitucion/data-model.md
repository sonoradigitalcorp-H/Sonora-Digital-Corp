# Data Model: Constitución
**Spec**: spec.md
---
## Entidades
| Entidad | Atributos | Descripción |
|---------|-----------|-------------|
| Constitution | id, version, date, status | Documento constitucional vinculante |
| Principle | id, name, description | Principio rector del desarrollo |
| Spec | id, title, status, created_at | Especificación SDD |
## Relaciones
```
(Constitution)-[:GOVERNS]->(Spec)
(Principle)-[:APPLIES_TO]->(Spec)
```
