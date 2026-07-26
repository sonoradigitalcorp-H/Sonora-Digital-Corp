---
title: "ADR-001: Estrategia de Memoria (3 Capas)"
date: 2026-07-25
status: accepted
author: SDC Architecture Team
version: 1.0.0
---

# ADR-001: Estrategia de Memoria

## Contexto

Mystic OS necesita un sistema de memoria que:

- Sea **barato** para conversaciones activas (muchas lecturas/escrituras)
- Sea **rápido** para recuperar contexto inmediato
- Sea **persistente** para el historial completo del usuario
- Permita **búsqueda semántica** para recordar conversaciones por tema
- Escale a cientos de tenants sin costo lineal

## Decisión

Implementar **3 capas de memoria**:

| Capa | Motor | Costo | Velocidad | Persistencia |
|------|-------|-------|-----------|-------------|
| Short-term | SQLite (archivo local) | Casi cero | Instantáneo | Sesión actual |
| Long-term | PostgreSQL | Bajo | Rápido | Indefinida |
| Semantic | Qdrant (vectores) | Medio | Medio | Indefinida |

### Alternativas Consideradas

1. **MongoDB sola**: buena para documentos, no tiene búsqueda semántica nativa
2. **Redis sola**: rápida pero no persistente para largo plazo
3. **PostgreSQL sola**: buena para SQL, embeddings son posibles con pgvector pero sin la eficiencia de Qdrant
4. **Qdrant sola**: excelente para búsqueda semántica, no ideal para historial secuencial

## Consecuencias

### Positivas

- **Aislamiento**: cada capa tiene un propósito claro y optimizado
- **Costo**: SQLite es esencialmente gratis, PostgreSQL es eficiente, Qdrant se escala bajo demanda
- **Rendimiento**: consultas de corto plazo no compiten con las de largo plazo
- **Flexibilidad**: cada capa puede reemplazarse independientemente

### Negativas

- **Complejidad**: 3 sistemas de almacenamiento que mantener
- **Latencia de escritura**: escribir en 3 lugares (aunque en background)
- **Consistencia**: posible desfase temporal entre capas

### Mitigaciones

- Las escrituras a long-term y semantic son **asíncronas** (cola de tareas)
- El MemoryEngine abstrae las 3 capas — el planner no sabe cuántas capas hay
- Cada capa tiene índices optimizados para su tipo de consulta

## Estado

**Aceptado**. Implementación progresiva: Short-term primero, luego Long-term, luego Semantic.
