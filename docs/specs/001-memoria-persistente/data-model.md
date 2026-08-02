# Data Model: Memoria Persistente
**Spec**: spec.md
---
## Entidades
| Entidad | Atributos | Descripción |
|---------|-----------|-------------|
| Session | id, title, pinned, project, tags, created_at, token_count | Conversación o hilo |
| Message | id, role, content, tokens, timestamp | Mensaje individual en sesión |
| Memory | key, value, timestamp | Par clave-valor persistente |
| Document | id, text, source, embedding[768] | Fragmento chunked para RAG |
## Relaciones
```
(Session)-[:CONTAINS]->(Message)
(Session)-[:HAS_MEMORY]->(Memory)
(Document)-[:EMBEDDED_IN]->(Qdrant:Collection)
```
