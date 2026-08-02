---
type: project
title: "{{title}}"
status: active
tags: [project, active]
created: {{date}}
---

# {{title}}

## Objetivo
{{qué se quiere lograr}}

## Estado
{{en qué fase está}}

## Próximos pasos
- [ ] Paso 1
- [ ] Paso 2

## Recursos
{{enlaces, archivos, referencias}}

## Decisiones relacionadas
```dataview
TABLE title, status, created
FROM "Decisions"
WHERE content contains "{{title}}"
```
