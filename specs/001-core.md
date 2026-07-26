---
title: Core del Sistema
date: 2026-07-25
status: draft
author: SDC Architecture Team
version: 1.0.0
---

# Core — SessionManager, MemoryEngine, Identidad

## SessionManager

El SessionManager es el punto de entrada de toda solicitud. Gestiona el ciclo de vida completo de la sesión.

### Responsabilidades

- Crear y validar sesiones por tenant
- Asignar `session_id`, `user_id`, `tenant_id` a cada request
- Mantener estado de sesión en Redis (TTL configurable)
- Limpiar sesiones expiradas

### Flujo

```
Request → Gateway → SessionManager.authenticate() → { session_id, user_id, tenant_id }
```

### API

```python
class SessionManager:
    def create_session(user_id: str, tenant_id: str) -> Session: ...
    def get_session(session_id: str) -> Optional[Session]: ...
    def validate_session(session_id: str) -> bool: ...
    def invalidate_session(session_id: str): ...
```

## MemoryEngine

El MemoryEngine abstrae las 3 capas de memoria detrás de una interfaz unificada.

### Capas

| Capa | Almacenamiento | TTL | Propósito |
|------|---------------|-----|-----------|
| Short-term | SQLite local | Sesión actual | Conversación activa, contexto inmediato |
| Long-term | PostgreSQL | Indefinido | Historial completo por usuario/tenant |
| Semantic | Qdrant | Indefinido | Embeddings, búsqueda vectorial, RAG |

### API

```python
class MemoryEngine:
    def store(tenant_id: str, user_id: str, entry: MemoryEntry): ...
    def recall_short_term(session_id: str, limit: int = 20) -> List[MemoryEntry]: ...
    def recall_long_term(tenant_id: str, user_id: str, query: str, limit: int = 10) -> List[MemoryEntry]: ...
    def recall_semantic(tenant_id: str, query: str, limit: int = 5) -> List[MemoryEntry]: ...
    def search_all(tenant_id: str, user_id: str, query: str) -> MemoryContext: ...
```

## Identidad

La identidad del usuario se mantiene en dos capas:

- **localStorage**: persiste `user_id` y `tenant_id` en el navegador (sobrevive a refrescos)
- **Server-side**: PostgreSQL guarda perfil, preferencias, historial de autenticación

### Flujo de autenticación

```
1. Frontend chequea localStorage → ¿hay user_id + tenant_id?
2. Si no → Gateway genera nuevo identity → se persiste en server + localStorage
3. Si sí → SessionManager valida contra Redis/PostgreSQL
4. Cada request incluye X-Tenant-ID + Authorization header
```

### Seguridad

- `tenant_id` se valida en cada request (middleware)
- Un tenant no puede acceder a datos de otro tenant
- Las sesiones expiran después de inactividad (configurable por tenant)
