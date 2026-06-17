# Feature Specification: ABE MUSIC

**Feature**: 011-abe-music
**Created**: 2026-06-09
**Status**: Implemented
**Input**: White label de SDC para sello discográfico digital. CRM artistas en grafos, dashboard CEO, revenue split, herramientas AI.

---

## Clarifications

| # | Question | Answer | Session |
|---|----------|--------|---------|
| 1 | ¿Revenue split? | 70% artista / 20% sello / 10% distribución | 011-01 |
| 2 | ¿Setup fee? | $5,000 + $500/mes mantenimiento | 011-01 |

---

## Infrastructure Mapping

| Component | File | Role |
|-----------|------|------|
| AgentOrchestrator | `src/core/orchestrator.py` | Rutear necesidades de artistas/CEO |
| Neo4j | `docker/neo4j/` | CRM grafos: Artist, Release, Collaboration |
| ABE MUSIC | `src/core/abe_music.py` | Lógica de negocio: CRM, KPIs, royalties |
| n8n | `config/n8n-sdc/music-hub/` | 5 workflows de distribución y marketing |
| Web UI | `webui/fastapp.py` | Dashboard CEO, endpoints API |

---

## User Stories

### US1 — Dashboard CEO (Priority: P1)

**Why This Priority**: El CEO necesita visibilidad para tomar decisiones

**Independent Test**: Crear artistas + releases + revenue → consultar dashboard → verificar KPIs.

**Acceptance Scenarios**:

1. **Given** artistas cargados, **When** se consulta dashboard, **Then** se ven KPIs totales (artistas, streams, revenue).
2. **Given** datos de revenue, **When** se calcula dashboard, **Then** top 5 artistas aparecen ordenados por revenue.
3. **Given** artistas inactivos, **When** se filtra por status, **Then** solo aparecen los del filtro.

### US2 — CRM de Artistas en Grafos (Priority: P1)

**Why This Priority**: El grafo permite descubrir colaboraciones y oportunidades

**Independent Test**: Crear artistas con relaciones → consultar grafo → verificar conexiones.

**Acceptance Scenarios**:

1. **Given** un artista creado, **When** se consulta por ID, **Then** se devuelven sus datos completos.
2. **Given** un release creado, **When** se registran streams, **Then** se acumulan en el artista.
3. **Given** revenue registrado, **When** se calcula split, **Then** artista recibe 70%.

### US3 — Revenue Split Automático (Priority: P2)

**Why This Priority**: Automatizar pagos a artistas evita errores y disputas

**Independent Test**: Registrar revenue de 3 fuentes distintas → verificar splits correctos.

**Acceptance Scenarios**:

1. **Given** revenue de streaming, **When** se registra, **Then** split es 70/20/10.
2. **Given** revenue de merch, **When** se registra, **Then** split es 60/30/10.
3. **Given** revenue de sync license, **When** se registra, **Then** split es 50/40/10.

---

## Edge Cases

- ¿Qué pasa si Stripe Connect no está configurado? Los splits se calculan pero no se pagan.
- ¿Qué pasa si un artista no tiene releases? Su KPI muestra ceros, no error.
- ¿Qué pasa si el revenue es 0? El split se calcula correctamente como 0.

---

## Requirements

### Functional Requirements *(mandatory)*

- **FR-001**: Sistema MUST almacenar artistas con género, país, status en Neo4j.
- **FR-002**: Sistema MUST tracking de streams y revenue por release y artista.
- **FR-003**: Sistema MUST calcular revenue split según fuente (streaming 70/20/10, merch 60/30/10, sync 50/40/10).
- **FR-004**: Sistema MUST exponer dashboard CEO con KPIs totales, top artists, revenue breakdown.
- **FR-005**: Sistema MUST exponer KPI individual por artista.

### Key Entities

- **Artist**: Artista musical con género, país, status (active/signed/development).
- **Release**: Lanzamiento (single/album/ep) con streams y revenue.
- **Revenue Entry**: Ingreso por fuente con split calculado.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Dashboard CEO carga KPIs correctos en < 2s.
- **SC-002**: Revenue split calculado correctamente para 3 fuentes distintas.
- **SC-003**: Stream tracking preciso: 100 streams = 100 contados.
- **SC-004**: 21 tests de unidad pasando.

---

## Assumptions

- Artistas tienen al menos un nombre y género para ser creados.
- Stripe Connect se usará para payout real.
- n8n workflows de music-hub están disponibles para distribución.
