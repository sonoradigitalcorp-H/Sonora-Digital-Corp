# Harvis OS — Constitución del Proyecto

## Principios Fundamentales

### I. Orquestación Única (Single Entry Point)

Todo input al sistema MUST entrar por un único punto: el Dispatcher.

- El Dispatcher es el ÚNICO componente que recibe requests externos (Telegram, Web, CLI, API)
- Ningún agente (OpenHands, OpenCode, Hermes, Aider) MUST comunicarse directamente con el usuario
- El humano solo aprueba o rechaza; nunca orquesta manualmente
- El flujo es: `Usuario → Dispatcher → Planner → Agente → QA → Respuesta`

**Razón**: Eliminar al humano como cuello de botella. Un sistema sin punto único de entrada genera caos y dependencia humana.

### II. Separación Determinista vs LLM

La lógica crítica de enrutamiento y toma de decisiones MUST ser determinista.

- El routing de tareas a agentes MUST implementarse con reglas deterministas (patterns, regex, lookup tables)
- El LLM solo se usa para: (a) clasificación de tareas ambiguas, (b) generación de planes, (c) explicaciones en lenguaje natural
- El LLM NUNCA debe decidir qué agente ejecuta una tarea cuando existe una regla clara
- La interfaz entre lógica determinista y LLM MUST ser explícita y unidireccional

**Razón**: Los LLMs son no deterministas. Confiar en ellos para routing crítico genera comportamiento impredecible y difícil de debuggear.

### III. Local-first por Defecto

Los datos del usuario y del sistema MUST permanecer locales por defecto.

- Los LLMs locales (Ollama) tienen prioridad sobre APIs externas
- Solo se usa API externa cuando el modelo local no puede resolver la tarea
- Ningún dato de tarea, resultado o contexto MUST salir del sistema sin acción explícita del usuario
- Las decisiones de routing NO dependen de servicios externos

**Razón**: Privacidad, control y costos. Un sistema que depende de APIs externas es frágil y costoso.

### IV. Testing Obligatorio

Cada componente MUST tener tests antes de ser considerado completo.

- El Dispatcher MUST tener tests de routing para cada patrón de tarea
- El Planner MUST tener tests de subdivisión de tareas
- Cada agente MUST tener tests de integración que verifiquen el contrato
- Los tests de lógica determinista MUST ser deterministas (sin dependencia de red o LLM)
- La cobertura mínima de la capa de lógica crítica es 80%

**Razón**: Sin tests, no hay garantía de corrección. Un sistema de orquestación con bugs destruye productividad en lugar de crearla.

### V. Trazabilidad Total

Cada tarea, decisión y resultado MUST ser trazable.

- Cada tarea recibe un ID único al crearla
- Cada decisión de routing se registra con timestamp, razón y patrón matcheado
- Cada resultado incluye: agente, duración, éxito/fallo, contexto usado
- El sistema MUST exponer un log de auditoría consulta por el usuario
- Ninguna decisión debe ser una caja negra

**Razón**: Sin trazabilidad, no hay debugging. Sin debugging, no hay mejora continua.

## Restricciones Adicionales

### Arquitectura

- El sistema MUST estar estructurado en capas: Gateway → Dispatcher → Planner → Agents → Infrastructure
- Cada capa solo se comunica con la capa adyacente
- Los agentes solo acceden a infraestructura a través de interfaces definidas
- El Event Bus (Redis Streams) es el medio de comunicación asíncrona

### Seguridad

- El sistema MUST ejecutarse bajo principios de mínimo privilegio
- Cada agente solo accede a los recursos que necesita
- No se permiten conexiones externas no declaradas
- Los secrets se manejan por variables de entorno, nunca en código

### Compatibilidad

- El sistema MUST ser compatible con los servicios existentes: OpenHands, OpenCode, Hermes, Aider, Telegram Bot, Qdrant, Neo4j, PostgreSQL, Redis
- NO se reemplazan servicios que ya funcionan; se integran
- La integración se hace a través de wrappers/adapters, no modificando el servicio original

## Flujo de Trabajo y Puertas de Calidad

### Constitution Check (Obligatorio antes de cada implementación)

```markdown
## Constitution Check — [Nombre de la Tarea]

### Principio I: Orquestación Única
- [ ] ¿Entra por Dispatcher?
- [ ] ¿No hay comunicación directa entre agentes?

### Principio II: Separación Determinista vs LLM
- [ ] ¿La lógica crítica es determinista?
- [ ] ¿El LLM solo se usa cuando es necesario?

### Principio III: Local-first
- [ ] ¿Los datos permanecen locales?
- [ ] ¿Se prioriza LLM local?

### Principio IV: Testing
- [ ] ¿Hay tests para esta funcionalidad?
- [ ] ¿Los tests cubren casos límite?

### Principio V: Trazabilidad
- [ ] ¿Cada decisión se registra?
- [ ] ¿Se puede auditar el flujo?
```

### Versionado

Esta Constitución sigue versionado semántico:

- **MAJOR**: eliminación o redefinición de principios
- **MINOR**: adición de nuevo principio o ampliación material
- **PATCH**: aclaraciones y correcciones de redacción

Toda enmienda MUST actualizar la versión, fecha y justificación.

## Gobernanza

Esta Constitución MUST tener precedencia sobre cualquier decisión técnica del proyecto. En caso de conflicto, el principio prevalece.

**Cómo resolver conflictos**:

1. Rediseñar la propuesta para cumplir el principio
2. Si no es posible, documentar la justificación y proponer enmienda
3. La propuesta MUST NO implementarse mientras contradiga un principio vigente

---

**Version**: 1.0.0
**Ratified**: 2026-08-04
**Last Amended**: 2026-08-04
**Author**: Luis Daniel Guerrero Enciso (Sonora Digital Corp)
