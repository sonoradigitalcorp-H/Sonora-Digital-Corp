---
title: Sistema de Memoria
date: 2026-07-25
status: draft
author: SDC Architecture Team
version: 1.0.0
---

# Memory — Short-term, Long-term, Semantic

## Visión General

Mystic OS registra **cada interacción** automáticamente. Antes de cada respuesta, recupera contexto relevante de las 3 capas. El resultado es un agente que recuerda conversaciones anteriores, preferencias del usuario, y conocimiento del dominio.

## Capas de Memoria

### 1. Short-term (SQLite local)

- **Ubicación**: archivo SQLite por sesión en el servidor
- **Contenido**: mensajes de la conversación activa (últimos 20 turnos)
- **TTL**: duración de la sesión (se descarta al cerrar)
- **Propósito**: contexto inmediato para coherencia conversacional

```sql
CREATE TABLE short_term_memory (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,       -- 'user' | 'assistant' | 'system' | 'tool'
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_short_term_session ON short_term_memory(session_id);
```

### 2. Long-term (PostgreSQL)

- **Ubicación**: tabla `long_term_memory` en PostgreSQL (sharded por tenant)
- **Contenido**: historial completo de interacciones del usuario
- **TTL**: indefinido
- **Propósito**: recuperar conversaciones anteriores, patrones de uso, preferencias

```sql
CREATE TABLE long_term_memory (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_long_term_tenant_user ON long_term_memory(tenant_id, user_id);
```

### 3. Semantic (Qdrant)

- **Ubicación**: colección Qdrant por tenant
- **Contenido**: embeddings de cada interacción (modelo `text-embedding-3-small` o similar)
- **TTL**: indefinido
- **Propósito**: búsqueda semántica — "encuentra conversaciones donde hablamos de X"

```python
QdrantCollection:
    name: "memory_{tenant_id}"
    vectors:
        size: 1536  # text-embedding-3-small
        distance: Cosine
    payload:
        - user_id
        - session_id
        - role
        - content_preview (primeros 200 chars)
        - created_at
```

## Flujo de Almacenamiento

```
1. Usuario envía mensaje
2. Mensaje se guarda en short-term (SQLite) inmediatamente
3. Mensaje se guarda en long-term (PostgreSQL) en background
4. Embedding se genera y guarda en Qdrant en background
5. Respuesta del asistente sigue el mismo flujo
```

## Flujo de Recuperación

```
Antes de cada respuesta:

1. Planner inicia MemoryEngine.search_all(tenant_id, user_id, query)
2. Short-term: últimos 20 mensajes de la sesión actual
3. Long-term: últimas 10 interacciones del usuario (por fecha)
4. Semantic: top 5 resultados por similitud coseno
5. Los 3 resultados se combinan en un MemoryContext
6. MemoryContext se inyecta en el prompt del LLM
```

## Aislamiento Multi-tenant

- Cada tenant tiene su propia colección en Qdrant
- Las consultas PostgreSQL usan `WHERE tenant_id = ?`
- Short-term es específica de sesión (no cross-tenant)
