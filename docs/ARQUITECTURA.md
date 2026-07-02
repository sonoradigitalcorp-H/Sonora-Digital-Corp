# Mapa de Arquitectura — Sonora Digital Corp

## Cerebro del Sistema

```
                        ┌─────────────────────────────────────┐
                        │         🧠  MCP ORCHESTRATOR          │
                        │   (Capa de comunicacion entre agentes) │
                        └──────────┬──────────────┬────────────┘
                                   │              │
              ┌────────────────────┼──────────────┼────────────────────┐
              │                    │              │                    │
              ▼                    ▼              ▼                    ▼
   ┌──────────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
   │    🤖 AGENTES     │  │   📡 MCP     │  │   🎵 ABE    │  │  🔧 OPS     │
   │   JARVIS Core     │  │   Servers    │  │   Music OS   │  │  Monitoreo  │
   │   18 agentes      │  │  Hermes,     │  │   Pipeline   │  │  Self-heal  │
   │   OpenClaw        │  │  Playwright  │  │   Sync       │  │  Alertas    │
   └────────┬─────────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
            │                   │                  │                 │
            └───────────────────┼──────────────────┼─────────────────┘
                                │                  │
                     ┌──────────▼──────────────────▼──────────┐
                     │          💾 CAPA DE DATOS               │
                     │  7 almacenes, cada uno con un proposito │
                     └─────────────────────────────────────────┘
```

---

## 7 Almacenes de Datos — Diferenciación Clara

### 1. 🟢 Neo4j — Grafos de Conocimiento (Relaciones Semánticas)

| Propiedad | Valor |
|-----------|-------|
| **Puerto** | 7687 (Bolt) / 7474 (HTTP) |
| **Tipo** | Graph Database (Nodos + Relaciones) |
| **Propósito** | Memoria relacional del sistema. Quién se conecta con qué. |
| **Qué guarda** | Personas, Conversaciones, Proyectos, Tareas, Conceptos, y sus relaciones |
| **Quién escribe** | JARVIS agents (MemoryAgent), n8n, ABE lead bridge |
| **Quién lee** | MemoryAgent, RAG engine, OpenClaw agents |
| **Query ej** | `MATCH (p:Person)-[:WORKS_ON]->(pr:Project) RETURN p, pr` |
| **Persistencia** | Docker volume `infra_neo4j_data` |
| **Estado** | 🟢 Funcionando (recién reparado) |

**Analogía**: Un mapa de metro. Muestra estaciones (nodos) y cómo se conectan (relaciones). No es rápido para búsqueda textual, pero es excelente para navegar relaciones.

---

### 2. 🔵 Qdrant — Vectores (RAG / Búsqueda Semántica)

| Propiedad | Valor |
|-----------|-------|
| **Puerto** | 6333 (gRPC) / 6334 (HTTP) |
| **Tipo** | Vector Database (Embeddings) |
| **Propósito** | Búsqueda por similitud semántica. "Encontrar cosas parecidas a esto" |
| **Qué guarda** | Embeddings de artistas, documentos, conversaciones |
| **Colecciones** | `abe-artists` (5 artistas), `abe-business` (5 negocios) |
| **Quién escribe** | `scripts/seed-qdrant.py`, JARVIS RAG engine |
| **Quién lee** | Abraham via ABE Service, agentes via RAG |
| **Query ej** | `search(collection="abe-artists", query_vector=[...], limit=5)` |
| **Persistencia** | Docker volume `infra_qdrant_storage` |
| **Estado** | 🟢 Funcionando, 2 colecciones |

**Analogía**: Un cerebro que encuentra cosas "parecidas a" lo que buscas. No sabe qué son las cosas, sabe cuáles se parecen entre sí.

---

### 3. 🐘 PostgreSQL — Datos Relacionales (Transacciones)

| Propiedad | Valor |
|-----------|-------|
| **Puerto** | 5432 |
| **Tipo** | Relational Database (SQL) |
| **Propósito** | Datos estructurados con esquema fijo. Transacciones ACID. |
| **Qué guarda** | Datos de LangFuse (traza de LLM), sesiones, usuarios |
| **Quién escribe** | LangFuse, ABE Service |
| **Quién lee** | LangFuse dashboard, debugging |
| **Persistencia** | Docker volume |
| **Estado** | 🟢 Funcionando |

**Analogía**: Una hoja de cálculo gigante con reglas estrictas. Cada columna tiene un tipo definido. No puedes poner texto donde va un número.

---

### 4. 🟠 Redis — Cache y Streams (En Memoria)

| Propiedad | Valor |
|-----------|-------|
| **Puerto** | 6379 |
| **Tipo** | In-Memory Data Store |
| **Propósito** | Caché ultrarrápido, colas de mensajes, rate limiting |
| **Qué guarda** | Sesiones temporales, colas de eventos, tokens rate-limit |
| **Quién escribe** | JARVIS agents, Hermes MCP |
| **Quién lee** | JARVIS agents, rate limiter |
| **Persistencia** | Opcional (RDB/AOF) — por defecto volátil |
| **Estado** | 🟢 Funcionando |

**Analogía**: La memoria RAM del sistema. Muy rápida, pero si se apaga, los datos se pierden. Ideal para colas y cachés.

---

### 5. 🗄️ SQLite (Engram) — Memoria Persistente Local

| Propiedad | Valor |
|-----------|-------|
| **Archivo** | `engram.db` |
| **Tipo** | Embedded SQL Database (FTS5 full-text search) |
| **Propósito** | Memoria de largo plazo del sistema. Lo que los agentes "recuerdan". |
| **Qué guarda** | Decisiones anteriores, errores, lecciones aprendidas, contexto de sesiones |
| **Quién escribe** | MemoryAgent, pipeline bridge, self-improvement system |
| **Quién lee** | MemoryAgent, context queries, score system |
| **Query ej** | `SELECT * FROM memories WHERE text MATCH 'capability registry decision engine'` |
| **Persistencia** | Archivo en disco (`engram.db`) |
| **Estado** | 🟢 Funcionando |

**Analogía**: El cuaderno de notas del sistema. No es rápido para relaciones complejas, pero guarda todo el contexto histórico con búsqueda por texto.

---

### 6. 📁 JSON Files — Configuración y Datos Estáticos

| Archivo | Propósito |
|---------|-----------|
| `data/abe-music.json` | Fuente de verdad de artistas, streams, revenue |
| `data/abe-contracts.json` | Contratos digitales |
| `data/abe-distribution.json` | Distribución y splits |
| `data/abe-ledger.json` | Revenue ledger |
| `config/registry.json` | Capability Registry v2 |
| `config/machines.json` | Máquinas y personas del sistema |
| `state/logs/events.jsonl` | Eventos auditables del pipeline |

**Analogía**: Documentos en una carpeta. Fáciles de leer, difíciles de consultar. Buenos para backup, malos para queries complejas.

---

### 7. 📝 Memory/Learning — Memoria de Agentes

| Archivo | Propósito |
|---------|-----------|
| `memory/learning/events.jsonl` | Eventos del sistema (sync, errores, decisiones) |
| `memory/learning/session-*.json` | Resúmenes de sesiones de trabajo |
| `memory/learning/rules.json` | Reglas del sistema |

**Analogía**: El diario del sistema. Cada agente puede leerlo para saber qué pasó antes de que él existiera.

---

## Diagrama de Flujo de Datos

```
                            ┌──────────────────┐
                            │   Ollama (LLM)    │
                            │  deepseek-r1:7b   │
                            │  qwen3:4b         │
                            │  nomic-embed      │
                            └────────┬─────────┘
                                     │
              ┌──────────────────────┼──────────────────────────┐
              │                      │                          │
              ▼                      ▼                          ▼
   ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────────┐
   │   Neo4j (Grafos)  │   │  Qdrant (Vector) │   │   Postgres (SQL)     │
   │   Relaciones      │   │  Embeddings      │   │   LangFuse trace     │
   │   "quien conoce a │   │  busqueda        │   │   Sesiones           │
   │    quien"         │   │  semantica       │   │   ACID               │
   └──────────────────┘   └──────────────────┘   └──────────────────────┘
              │                      │                          │
              └──────────────────────┼──────────────────────────┘
                                     │
                                     ▼
                          ┌────────────────────┐
                          │    Engram (SQLite)  │
                          │    Memoria persist. │
                          │    Contexto histor. │
                          └────────────────────┘
                                     │
                                     ▼
                          ┌────────────────────┐
                          │  JSON files (backup)│
                          │  data/abe-music.json│
                          │  state/logs/        │
                          └────────────────────┘
```

## Reglas de Oro

| Regla | Explicación |
|-------|-------------|
| **Neo4j** = relaciones | Usa grafos cuando la pregunta es "cómo se conecta X con Y" |
| **Qdrant** = similitud | Usa vectores cuando la pregunta es "qué es parecido a X" |
| **Postgres** = estructura | Usa SQL cuando los datos tienen esquema fijo y necesitas consistencia |
| **Redis** = velocidad | Usa Redis cuando necesitas respuesta en <1ms o colas de mensajes |
| **Engram** = memoria | Usa Engram cuando necesitas que el sistema "recuerde" el pasado |
| **JSON** = backup | Usa JSON para config, backup, y datos que lee Abraham |
| **Memory/Learning** = contexto | Usa memory/ para que los agentes sepan lo que pasó en sesiones anteriores |
