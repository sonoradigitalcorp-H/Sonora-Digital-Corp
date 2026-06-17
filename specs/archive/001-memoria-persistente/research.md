# Research: Memoria Persistente
**Spec**: spec.md
---
## Tecnologías Evaluadas
| Opción | Ventajas | Desventajas | Decisión |
|--------|----------|-------------|----------|
| Neo4j 5.19 | Grafos, APOC, comunidad, GraphRAG | Recurso intensivo | ✅ Seleccionado |
| Qdrant | Open source, dockerizado, payload indexing | Solo vectores | ✅ Complemento vectorial |
| ChromaDB | Ligero, embedido | Menos features | ❌ Descartado |
| Pinecone | SaaS, zero mantenimiento | Costo, datos en nube | ❌ Descartado |
## Decisión Arquitectónica
- **Selección**: Neo4j (grafos) + Qdrant (vectores) + in-memory (fallback)
- **Motivo**: Separación clara entre conocimiento relacional y semántico
## Limitaciones
1. Embeddings 768d limitan granularidad semántica
2. Sin Redis, la memoria in-memory no persiste entre reinicios
