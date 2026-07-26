# ADR-20260721-CRM-ARCHITECTURE — CRM Module Architecture

| Campo | Valor |
|-------|-------|
| ID | `ADR-20260721-CRM-ARCHITECTURE` |
| Fecha | 2026-07-21 |
| Spec | `SPEC-CRM-001` |
| Estado | aceptado |

## Context

Cada cliente necesita un sistema de gestión de contactos con CRM, RAG personal, y memoria persistente. El sistema debe:
- Almacenar contactos con ID único, nombre, teléfono, empresa
- Búsqueda rápida por nombre/teléfono/empresa
- Sincronizar a Engram (memoria primaria), Qdrant (vectores), Neo4j (grafos)
- Emitir eventos en tiempo real para contexto compartido

## Decision

Se implementa un CRM modular SQLite local (siempre disponible) con sync asíncrono a las capas de memoria:

```
CRM SQLite (primary store, always available)
  → Engram (layer 3 - customer, sync)
  → Qdrant (vector index, best effort)
  → Neo4j (knowledge graph, best effort)
  → Events JSONL (streaming log)
```

El CRM usa un ID generado con formato `CT-{timestamp_ms}-{uuid_hex8}` para identificar contactos de forma única. La búsqueda usa SQLite LIKE+FTS con ranking por relevancia.

## Options Considered

| Opción | Pros | Contras |
|--------|------|---------|
| SQLite local + sync | Sin dependencias de red, siempre disponible, fácil backup | No distribuido, límite de un escritor |
| Solo PostgreSQL/Neo4j | Escalable, accesible desde múltiples servicios | Dependencia de red, latencia, single point of failure |
| MongoDB | Flexible schema, buen search | Dependencia extra, no disponible actualmente |

## Consequences

- CRM siempre disponible incluso si Qdrant/Neo4j caen
- Los contactos nuevos se sincronizan automáticamente a todas las capas
- Engram es la fuente de verdad para consultas RAG
- Se necesita re-sync si alguna capa se restaura desde backup

## Lessons

- Separar storage (SQLite) de sync (HTTP) permite tolerancia a fallos
- El formato de ID con timestamp permite ordenar cronológicamente sin campo extra
- Los errores de sync no deben propagarse al usuario (best effort)

## Related

- Skills: `skills/crm-client.skill.md`
- Módulo: `clients/aztrotech/crm/`
- Eventos: `crm:contact:upserted`
