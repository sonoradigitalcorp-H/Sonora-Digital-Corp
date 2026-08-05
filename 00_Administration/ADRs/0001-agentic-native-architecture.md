# ADR 0001: Arquitectura Agentic Native Multitenant
## Contexto
Se requiere escalabilidad absoluta y aislamiento de clientes.
## Decisión
Adoptar una arquitectura donde Hermes (Nous) es el orquestador, Engram la memoria episódica, Qdrant la memoria semántica (RAG) y Neo4j la memoria relacional. Todo desplegado localmente.
## Estado
Aceptado.