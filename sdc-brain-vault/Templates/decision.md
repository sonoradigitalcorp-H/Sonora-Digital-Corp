---
type: decision
title: "{{title}}"
status: active
tags: [decision, active]
created: {{date}}
---

# {{title}}

## Contexto
{{qué llevó a esta decisión}}

## Decisión
{{qué se decidió}}

## Alternativas consideradas
{{opciones que se evaluaron}}

## Consecuencias
{{qué pasó después}}

## Relaciones
```dataview
TABLE type, project
FROM "Observations"
WHERE topic_key = "{{title}}"
```
