# Data Model: Infraestructura y Seguridad
**Spec**: spec.md
---
## Entidades
| Entidad | Atributos | Descripción |
|---------|-----------|-------------|
| Service | name, status, port, type | Servicio del sistema |
| Secret | key, value (encrypted), scope | Credencial sensible |
| Backup | id, path, size, date, type | Punto de restauración |
| Log | timestamp, level, source, message | Registro de evento |
## Relaciones
```
(Service)-[:USES]->(Secret)
(Backup)-[:OF]->(Service)
```
