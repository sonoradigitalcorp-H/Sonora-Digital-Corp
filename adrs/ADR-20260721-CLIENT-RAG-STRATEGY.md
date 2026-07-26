# ADR-20260721-CLIENT-RAG-STRATEGY — Client RAG Memory Strategy

| Campo | Valor |
|-------|-------|
| ID | `ADR-20260721-CLIENT-RAG-STRATEGY` |
| Fecha | 2026-07-21 |
| Status | aceptado |

## Context

Cada cliente necesita un RAG (Retrieval-Augmented Generation) personal que incluya:
- Datos de CRM (nombre, empresa, teléfono)
- Historial de conversaciones
- Preferencias, herramientas y skills asignadas
- Conocimiento del negocio del cliente
- Memoria a corto, mediano y largo plazo

## Decision

### Arquitectura de memoria por plazos

| Plazo | Capa | Store | TTL | Ejemplo |
|-------|------|-------|-----|---------|
| Corto (Working) | Layer 0 | Engram + Events | Sesión | Último mensaje, contexto activo |
| Mediano (Project) | Layer 2-3 | Engram + CRM | 30 días | Preferencias del cliente, tools asignadas |
| Largo (Customer) | Layer 3-4 | Engram + Qdrant + Neo4j | Permanente | Historial completo, skills creadas |

### RAG pipeline por cliente

```
CRM Contact (SQLite)
  → Engram (contact:{crm_id} — layer 3, customer memory)
  → Qdrant (kb_{tenant} — vector embeddings para semantic search)
  → Neo4j (Contact → BELONGS_TO → Tenant, + :HAS_SKILL, :USES_TOOL edges)
  → Events (crm:rag:updated — streaming log)
```

### Skills y tools tracking

Cada cliente puede tener:
- `skills/` personalizadas (skill files por cliente)
- Tools MCP habilitadas
- Preferencias de canales (telegram, whatsapp, web)
- Gustos y notas personales

## Options Considered

| Opción | Pros | Contras |
|--------|------|---------|
| Engram + Qdrant + Neo4j multi-capa | Separación de concerns, cada store optimizado para su tipo de query | Complejidad operativa, 3 stores que mantener |
| Solo Engram con FTS | Simple, siempre disponible | Sin vector search, sin graph traversal |
| Solo Qdrant | Buen semantic search | Sin relaciones, sin memoria estructurada |

## Consequences

- Se necesita mantener 3 stores sincronizados
- Engram es la fuente de verdad primaria
- Qdrant permite "encuentra clientes similares a X"
- Neo4j permite "qué skills tiene este cliente" y "qué otros clientes usan esta tool"
- La limpieza de TTLs debe hacerse periódicamente

## Related

- ADR: `ADR-20260721-CRM-ARCHITECTURE`
- Skills: `skills/crm-client.skill.md`
- Stores: Engram, Qdrant (port 6333), Neo4j (port 7687)
