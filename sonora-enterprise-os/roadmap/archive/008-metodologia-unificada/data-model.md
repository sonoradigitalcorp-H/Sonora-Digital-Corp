# Data Model: Metodología Unificada
**Spec**: spec.md
---
## Entidades
| Entidad | Atributos | Descripción |
|---------|-----------|-------------|
| MethodologyCommand | name, type, steps, output | Comando de metodología (GSD, wrap-up, etc.) |
| Experience | id, error_pattern, solution, confidence | Lección aprendida |
| Improvement | id, agent, rule, diff, applied | Mejora propuesta a agente |
## Relaciones
```
(MethodologyCommand)-[:GENERATES]->(Experience)
(Experience)-[:TRIGGERS]->(Improvement)
```
