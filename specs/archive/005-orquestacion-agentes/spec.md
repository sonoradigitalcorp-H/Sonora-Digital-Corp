# Feature Specification: Orquestación de Agentes

**Feature**: 005-orquestacion-agentes
**Status**: Active
**Input**: JARVIS necesita un sistema de agentes especializados que reciban tareas, las ejecuten con las herramientas disponibles, y devuelvan resultados estructurados.

---

## User Stories

### US11 — Delegar tareas al agente correcto
El usuario pide algo y JARVIS automáticamente elige el agente especializado más adecuado para resolverlo.

**Prioridad**: P1
**Dependencias**: 002-servidor-mcp (tools)

**Independent Test**: Llamar al orquestador con la frase "buscá información sobre X" — verificar que el agente seleccionado es ResearchAgent. Testeable sin LLM ni servicios externos.

**Acceptance Scenarios**:
1. **Given** un usuario que pide "buscá información sobre X", **When** se procesa la tarea, **Then** se enruta a ResearchAgent.
2. **Given** un usuario que pide "escribí una función que haga Y", **When** se procesa, **Then** se enruta a CodeAgent.
3. **Given** un usuario que pide "revisá este código", **When** se procesa, **Then** se enruta a ReviewAgent.
4. **Given** una tarea que no coincide con ningún agente, **When** se procesa, **Then** se enruta a ResearchAgent (default).

### US12 — CodeAgent: analizar, generar, leer y corregir código
El usuario pide analizar, generar, leer o corregir código, y CodeAgent lo ejecuta usando las tools del sistema.

**Prioridad**: P1
**Dependencias**: US11

**Independent Test**: Llamar a CodeAgent con "analizá src/core/llm.py" — debe devolver métricas (líneas, funciones, complejidad). Testeable sin LLM.

**Acceptance Scenarios**:
1. **Given** una ruta de archivo, **When** el usuario pide analizarlo, **Then** CodeAgent devuelve métricas (líneas, funciones, complejidad).
2. **Given** una descripción de tarea, **When** el usuario pide generar código, **Then** CodeAgent escribe el archivo usando el LLM.
3. **Given** una ruta de archivo, **When** el usuario pide leerlo, **Then** CodeAgent devuelve el contenido.
4. **Given** un bug descrito, **When** el usuario pide corregirlo, **Then** CodeAgent lee, genera fix, escribe y verifica.

### US13 — MemoryAgent: recordar y gestionar contexto
El usuario pide guardar o recuperar información contextual, y MemoryAgent lo gestiona.

**Prioridad**: P1
**Dependencias**: 001-memoria-persistente

**Independent Test**: Llamar a MemoryAgent con "guardá que mi color favorito es azul", luego "recordá mi color favorito" — debe devolver "azul". Testeable con o sin Neo4j (fallback in-memory).

**Acceptance Scenarios**:
1. **Given** un dato que el usuario quiere recordar, **When** lo guarda, **Then** persiste en Neo4j (o in-memory).
2. **Given** un dato previamente guardado, **When** el usuario pregunta por él, **Then** MemoryAgent lo recupera.
3. **Given** un dato que el usuario quiere olvidar, **When** lo pide, **Then** MemoryAgent lo elimina.

### US14 — Revisar, explorar, ejecutar skills y voz
Los agentes ReviewAgent, ExploreAgent, SkillAgent y VoiceAgent manejan tareas especializadas.

**Prioridad**: P2
**Dependencias**: US11

**Independent Test**: Llamar a ExploreAgent con "explorá src/" — debe devolver estructura de árbol del directorio. Testeable sin dependencias externas.

**Acceptance Scenarios**:
1. **Given** un archivo, **When** ReviewAgent lo revisa, **Then** devuelve issues y score (1-10).
2. **Given** una ruta de directorio, **When** ExploreAgent la explora, **Then** devuelve estructura de árbol.
3. **Given** un nombre de skill, **When** SkillAgent la ejecuta, **Then** devuelve el resultado.
4. **Given** un texto, **When** VoiceAgent lo dice, **Then** el TTS (si disponible) lo reproduce.

---

### Edge Cases

- ¿Qué pasa si todos los agentes están ocupados? El orquestador MUST encolar la tarea y procesarla cuando haya un agente disponible.
- ¿Qué pasa si una tarea no coincide con ningún agente? MUST enrutar a ResearchAgent (default) con mensaje informativo.
- ¿Qué pasa si un agente excede su timeout? MUST cancelar y devolver error con el progreso parcial si existe.
- ¿Qué pasa si se intenta ejecutar una tarea sin herramientas disponibles? MUST devolver error claro indicando qué tool falta.
- ¿Qué pasa si hay keywords que coinciden con múltiples agentes? MUST usar la coincidencia más específica (mayor número de keywords).
- ¿Qué pasa si el orquestador recibe una tarea malformada (sin texto)? MUST rechazar con mensaje de validación.

---

## Requirements

### Functional Requirements

**FR-040**: El sistema MUST implementar 7 agentes: ResearchAgent, CodeAgent, ExploreAgent, MemoryAgent, SkillAgent, VoiceAgent, ReviewAgent.
**FR-041**: Cada agente MUST heredar de `AgentBase` con métodos `run(task)` async, `name`, `description` y `timeout`.
**FR-042**: El AgentOrchestrator MUST enrutar tareas por keywords con regex word-boundary.
**FR-043**: El AgentOrchestrator MUST soportar ejecución secuencial y paralela de tareas.
**FR-044**: ResearchAgent MUST buscar en Neo4j y Qdrant combinando resultados.
**FR-045**: CodeAgent MUST soportar 4 modos: analyze, generate, read, fix_bug.
**FR-046**: ExploreAgent MUST listar archivos, buscar código, mostrar estructura de árbol.
**FR-047**: ReviewAgent MUST analizar código y devolver issues categorizados con score (1-10).
**FR-048**: Los agentes MUST tener timeout configurable por agente.

### Key Entities

- **AgentBase**: Clase base abstracta con `run()`, `name`, `description`, `timeout`.
- **AgentOrchestrator**: Singleton que contiene todos los agentes y los enruta por keywords.
- **Routing Rule**: Tupla (lista_de_keywords, nombre_del_agente).

---

## Success Criteria

- **SC-040**: Routing funciona para 15+ frases de prueba cubriendo todos los agentes.
- **SC-041**: Cada agente devuelve respuesta en < timeout definido.
- **SC-042**: CodeAgent genera código válido que puede escribirse y leerse.
- **SC-043**: ReviewAgent identifica TODOs, FIXMEs, líneas largas y debug statements.
- **SC-044**: Todos los agentes devuelven `status: "success"` en caso normal y `status: "error"` con mensaje en caso de error.

---

## Assumptions

- Los agentes ejecutan tareas que pueden ser bloqueantes (sync) dentro de métodos async.
- El routing es por matching de palabras clave, no por análisis semántico.
- Los timeouts evitan que un agente cuelgue el orquestador.
