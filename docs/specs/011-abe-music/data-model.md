# Data Model: ABE MUSIC
**Spec**: spec.md
---
## Entidades
| Entidad | Atributos | Descripción |
|---------|-----------|-------------|
| Artist | id, nombre, genero, pais, status, streams, revenue | Artista musical |
| Release | id, artist_id, titulo, tipo, streams, revenue, status | Lanzamiento |
| RevenueEntry | id, release_id, amount, source, artist_share, label_share | Ingreso con split |
## Relaciones
```
(Artist)-[:RELEASED]->(Release)
(Release)-[:GENERO_INGRESO]->(RevenueEntry)
```
