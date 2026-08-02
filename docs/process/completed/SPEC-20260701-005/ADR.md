# ADR-20260701-005 — Arquitectura de Datos + Monitoreo + Neo4j Revival

| Campo | Valor |
|-------|-------|
| **ID** | `ADR-20260701-005` |
| **Fecha** | 2026-07-01 |
| **Spec** | `SPEC-20260701-005` |
| **Estado** | aceptado |

---

## Context

Neo4j estaba caído (Bolt handshake fallaba por escuchar solo en 127.0.0.1 dentro del contenedor). 
Los 7 almacenes de datos del sistema no estaban documentados ni diferenciados. 
No existía monitoreo automático de contenedores. 
Los agentes no tenían acceso a un grafo de conocimiento del sistema.

## Decision

### 1. Neo4j: bind a 0.0.0.0 + auth deshabilitado

El entrypoint personalizado de Neo4j no procesa `NEO4J_` env vars como el oficial. 
Se agregaron las configuraciones directamente en el Dockerfile via `RUN echo ... >> neo4j.conf`.

**Impacto**: Bolt ahora funciona desde el host. Auth deshabilitado (solo red interna, no expuesto).

### 2. Mapa de arquitectura (`docs/ARQUITECTURA.md`)

7 almacenes de datos diferenciados con:
- Propósito, puerto, tipo, quién escribe, quién lee, analogía
- Diagrama de flujo de datos
- Reglas de oro de cuándo usar cada uno

### 3. Monitoreo de contenedores (`scripts/monitor.py`)

Timer systemd que verifica todos los contenedores Docker cada 2 minutos.
Emite eventos `container_down` y `container_recovered` a events.jsonl.

### 4. Grafo del sistema en Neo4j (`scripts/seed-neo4j-arquitectura.py`)

19 nodos (3 personas, 13 servicios, 3 capabilities) y 19 relaciones.
Los agentes pueden consultar `MATCH (p:Person)-[:OWNS]->(s:Service)` directamente.

## Consequences

**Positivo:**
- Neo4j funcional y accesible desde cualquier servicio en el VPS
- Todos los almacenes de datos documentados con propósito claro
- Contenedores monitoreados automáticamente con alertas
- Grafo de conocimiento del sistema disponible para agentes

**Trade-offs:**
- Auth de Neo4j deshabilitado — seguro solo porque no está expuesto a internet
- Monitor no envía notificaciones externas aún (solo events.jsonl)

## Related

- Spec: `SPEC-20260701-005`
- Scripts: `scripts/monitor.py`, `scripts/seed-neo4j-arquitectura.py`
- Docs: `docs/ARQUITECTURA.md`
- Services: `monitor.timer`, `monitor.service`
