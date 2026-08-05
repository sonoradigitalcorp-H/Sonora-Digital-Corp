# Schema de Datos para Neo4j Graph Dashboard

## Nodos (Nodes)

### Tenant (Cliente)
```cypher
// :Tenant {name: "Aztrotech", status: "active", created_at: "2026-08-05"}
```

### Agente (Agent)
```cypher
// :Agent {name: "Hermes", model: "hermes-3", role: "orchestrator", status: "online"}
// :Agent {name: "Listener", model: "whisper-cli", role: "stt", status: "offline"}
// :Agent {name: "Speaker", model: "edge-tts", role: "tts", status: "offline"}
```

### Herramienta (Tool)
```cypher
// :Tool {name: "engram_memory", type: "MCP", status: "running"}
// :Tool {name: "whisper_stt", type: "CLI", status: "running"}
// :Tool {name: "qdrant_vector", type: "DB", status: "running"}
```

### Evento (Event)
```cypher
// :Event {id: "evt_001", type: "booking_attempt", status: "success", timestamp: "2026-08-10T14:30:00Z"}
```

### Skill
```cypher
// :Skill {name: "Aztrotech Voice Booking", version: "1.0", tenant: "Aztrotech"}
```

## Relaciones

```
(Tenant)-[:HAS_AGENT]->(Agent)
(Agent)-[:USES_TOOL]->(Tool)
(Agent)-[:HAS_SKILL]->(Skill)
(Tenant)-[:EXECUTES]->(Event)
(Event)-[:TRIGGERED_BY]->(Agent)
(Event)-[:ACCESSED]->(Tool)
(Tenant)-[:HAS_MEMORY]->(:Tool {type: "MCP"})
```

## Queries de Auditoría (para Sergio Durán)

### 1. Vista General del Sistema
```cypher
MATCH (t:Tenant)-[:HAS_AGENT]->(a:Agent)-[:USES_TOOL]->(tool:Tool)
RETURN t.name AS Cliente, 
       collect(DISTINCT a.name) AS Agentes,
       collect(DISTINCT tool.name) AS Herramientas
ORDER BY t.name
```

### 2. Trazabilidad de una Skill Específica
```cypher
MATCH (t:Tenant {name: "Aztrotech"})-[:HAVE_SKILL]->(s:Skill)
MATCH (s)<-[:TRIGGERED_BY]-(e:Event)-[:TRIGGERED_BY]->(a:Agent)-[:USES_TOOL]->(tool:Tool)
RETURN e.id AS Evento, e.type AS Tipo, e.status AS Estado,
       a.name AS Agente, tool.name AS Herramienta,
       e.timestamp AS Timestamp
ORDER BY e.timestamp DESC
LIMIT 10
```

### 3. Estado de Salud de Herramientas
```cypher
MATCH (tool:Tool)
RETURN tool.name AS Herramienta, 
       tool.type AS Tipo, 
       tool.status AS Estado
ORDER BY tool.type, tool.name
```

## Dashboard JSON (para visualización)

Este archivo describe la estructura del grafo para el dashboard de auditoría.
Los datos reales se poblan vía el SDK al ejecutar skills.
