---
type: person
name: "{{title}}"
role: 
company: 
contact: 
tags: [person, active]
created: {{date}}
---

# {{title}}

## Rol
{{descripcion del rol y relación conmigo}}

## Contacto
- Teléfono:
- Email:
- WhatsApp:
- Redes:

## Notas
{{notas sobre esta persona}}

## Conexiones
```dataview
TABLE type, project, created_at
FROM "Observations"
WHERE content contains "{{title}}"
SORT created_at DESC
```
