# Data Model: Web UI
**Spec**: spec.md
---
## Entidades
| Entidad | Atributos | Descripción |
|---------|-----------|-------------|
| Session | id, title, pinned, messages[], token_count | Sesión de chat en UI |
| UITheme | name, colors, fonts | Tema visual (dark/light/cyberpunk) |
| FileNode | name, path, type, size, children[] | Nodo del explorador de archivos |
## Relaciones
```
(Session)-[:RENDERED_WITH]->(UITheme)
(FileNode)-[:PARENT_OF]->(FileNode)
```
