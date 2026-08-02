# Feature Specification: Metodología Unificada

**Feature**: 008-metodologia-unificada
**Status**: Active
**Input**: JARVIS necesita un stack metodológico completo que integre SDD (diseño), GSD (ejecución) y Self-Improve (mejora continua) para operar como un sistema de desarrollo autónomo y en evolución constante.

---

## User Stories

### US1 — GSD: Planificar y ejecutar proyectos completos
El usuario puede iniciar un proyecto desde cero y JARVIS ejecuta el flujo GSD: contexto profundo, investigación con 4 agentes paralelos, scoping de requirements, roadmap, fases, ejecución por waves y verificación goal-backward.

**Prioridad**: P1
**Dependencias**: OpenClaw Gateway accesible

**Independent Test**: Iniciar `/gsd new-project test` y verificar que se crea directorio `.planning/` con PROJECT.md, REQUIREMENTS.md, ROADMAP.md.

**Acceptance Scenarios**:
1. **Given** un request `/gsd new-project`, **When** JARVIS ejecuta GSD, **Then** crea `.planning/` con documentos de planificación.
2. **Given** un proyecto en ejecución, **When** se completa una fase, **Then** se actualiza el roadmap con progreso.
3. **Given** un proyecto pausado, **When** se reanuda, **Then** se restaura el contexto completo.

### US2 — Close-Loop: Cerrar sesiones correctamente
Al finalizar una sesión de trabajo, JARVIS ejecuta el flujo close-loop: shippear cambios, consolidar memoria, aplicar auto-mejoras y generar reporte.

**Prioridad**: P1
**Dependencias**: GSD instalado

**Independent Test**: Ejecutar `/wrap-up` y verificar que se genera un reporte con ship state, memory consolidation y self-improvements aplicados.

**Acceptance Scenarios**:
1. **Given** cambios sin commit, **When** se ejecuta close-loop, **Then** se staggean y commitean.
2. **Given** una sesión con decisiones, **When** se ejecuta close-loop, **Then** se consolidan en memoria persistente.
3. **Given** reglas de auto-mejora pendientes, **When** se ejecuta close-loop, **Then** se aplican antes de cerrar.

### US3 — Learning-Loop: Auto-mejora estructurada
JARVIS mantiene un sistema de auto-mejora con confidence decay, cross-agent sharing y anomaly detection.

**Prioridad**: P2
**Dependencias**: Close-Loop instalado

**Independent Test**: Simular un error recurrente y verificar que learning-loop detecta el patrón y sugiere una mejora.

**Acceptance Scenarios**:
1. **Given** errores repetidos en una tarea, **When** learning-loop analiza, **Then** detecta el patrón con confidence score.
2. **Given** una mejora identificada, **When** cross-agent sharing está activo, **Then** la mejora se propaga a agentes relevantes.
3. **Given** anomalías en el comportamiento, **When** se detectan, **Then** se registran para revisión.

### US4 — Reflect: Mejora por análisis de conversaciones
JARVIS analiza las conversaciones en busca de señales de corrección y patrones exitosos, y propone cambios permanentes a sus archivos de configuración.

**Prioridad**: P2
**Dependencias**: Ninguna

**Independent Test**: Decir "nunca uses var en TypeScript" y luego ejecutar `reflect` — debe proponer un cambio al agente frontend.

**Acceptance Scenarios**:
1. **Given** una corrección explícita del usuario, **When** se ejecuta `reflect`, **Then** se genera un diff propuesto.
2. **Given** un diff aprobado, **When** se aplica, **Then** el cambio persiste en el archivo del agente.
3. **Given** múltiples sesiones, **When** reflect analiza, **Then** genera métricas de mejora continua.

### US5 — Agent-Evolver: Biblioteca de experiencia
JARVIS mantiene una biblioteca de experiencia en SQLite donde almacena lecciones aprendidas de errores pasados, consultable semánticamente.

**Prioridad**: P2
**Dependencias**: SQLite, ChromaDB (opcional)

**Independent Test**: Registrar un error, simular el mismo error, verificar que agent-evolver recupera la solución previa.

**Acceptance Scenarios**:
1. **Given** un error resuelto, **When** se registra en la experiencia library, **Then** queda disponible para consulta semántica.
2. **Given** un error recurrente, **When** se busca en la library, **Then** encuentra la solución previa con score de similitud.
3. **Given** una solución aplicada exitosamente, **When** se registra el outcome, **Then** se actualiza el success rate.

---

## Requirements

### Functional Requirements

**FR-001**: El sistema MUST tener GSD instalado como skill de OpenClaw y accesible desde el SkillAgent.
**FR-002**: El sistema MUST tener Close-Loop instalado y ejecutable al final de cada sesión.
**FR-003**: El sistema MUST tener Learning-Loop instalado para detección de patrones de error.
**FR-004**: El sistema MUST tener Reflect instalado para análisis de conversaciones y mejora de agentes.
**FR-005**: El sistema MUST tener Agent-Evolver instalado para biblioteca de experiencia.
**FR-006**: El sistema MUST exponer comandos `/gsd`, `/wrap-up`, `/reflect` y `/learn` en la Web UI.
**FR-007**: El sistema MUST integrar GSD en el SkillAgent del orquestador.
**FR-008**: El sistema MUST documentar el stack metodológico en SKILL_REGISTRY.md.

### Methodology Stack

```
┌────────────────────────────────────────────────────────┐
│                    SDD (Spec-Driven)                    │
│  specs/ · constitution · templates · checklists         │
│  Qué construir y por qué                               │
├────────────────────────────────────────────────────────┤
│                    GSD (Get Shit Done)                  │
│  gsd skill · .planning/ · waves · goal-backward        │
│  Cómo ejecutarlo                                       │
├────────────────────────────────────────────────────────┤
│              Self-Improve (Close-Loop)                  │
│  close-loop · learning-loop · reflect · agent-evolver  │
│  Cómo mejorar continuamente                            │
└────────────────────────────────────────────────────────┘
```

### Skill Integration Points

| Skill | Agente JARVIS | Comando | Output |
|-------|---------------|---------|--------|
| GSD | SkillAgent / OpenClawAgent | `/gsd` | `.planning/` directory |
| Close-Loop | SkillAgent | `/wrap-up` | Report + commit + memory |
| Learning-Loop | GbrainAgent | `/learn` | Pattern detection |
| Reflect | ReviewAgent | `/reflect` | Agent file diffs |
| Agent-Evolver | MemoryAgent | Auto | Experience library |

---

## Success Criteria

- **SC-001**: GSD instalado y ejecutable desde JARVIS
- **SC-002**: Close-Loop instalado y ejecutable
- **SC-003**: Learning-Loop instalado
- **SC-004**: Reflect instalado
- **SC-005**: Agent-Evolver instalado
- **SC-006**: Todos los skills registrados en SKILL_REGISTRY.md
- **SC-007**: 0 tests rotos después de la integración

---

## Edge Cases

- ¿Qué pasa si OpenClaw Gateway no está disponible? El SkillAgent MUST informar que el skill no está accesible y sugerir arrancar OpenClaw.
- ¿Qué pasa si GSD ya fue ejecutado y `.planning/` existe? GSD MUST restaurar el contexto existente en lugar de sobrescribir.
- ¿Qué pasa si no hay cambios para shippear en Close-Loop? El skill MUST saltar la fase de ship sin error.
- ¿Qué pasa si Reflect no encuentra señales de corrección? Debe informar "no se detectaron learning signals" sin crear archivos vacíos.
- ¿Qué pasa si Agent-Evolver no tiene SQLite? Debe fallback a JSON file-based storage.
