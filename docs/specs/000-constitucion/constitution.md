# JARVIS — Constitución del Proyecto

**Versión**: 1.0.0
**Ratificada**: 2026-06-09
**Última modificación**: 2026-06-09

---

## Principios Fundamentales

### I. Separación de Responsabilidades (Decisión Determinista vs. LLM)

La lógica de orquestación, routing y validación MUST ser 100% determinista, reproducible y testeable.

- El motor de decisión (orquestador, routing de agentes, tools, pipeline RAG) MUST estar implementado como código determinista sin dependencia de modelos generativos.
- El LLM MUST limitarse a generar respuestas y análisis a partir de datos **ya procesados**. El LLM MUST NOT decidir rutas, alterar estados ni ejecutar comandos sin validación determinista.
- La interfaz entre el motor determinista y el LLM MUST ser unidireccional: los datos fluyen hacia el LLM; nada producido por el LLM retroalimenta el estado del sistema sin pasar por validación.

**Razón**: La corrección y auditabilidad exigen decisiones verificables. Un LLM es no determinista por naturaleza y no puede ser la fuente de verdad del sistema.

### II. Privacidad y Control Local

Los datos del usuario MUST permanecer en la máquina local y MUST NOT transmitirse a servicios externos sin consentimiento explícito.

- La única conexión externa permitida es la llamada al LLM vía opencode-go/OpenRouter.
- Datos sensibles MUST estar en variables de entorno, nunca en código.
- Sin telemetría ni tracking externo.
- El usuario MUST tener control total sobre qué modelos y servicios se usan.

**Razón**: La privacidad es un derecho fundamental; el procesamiento local elimina superficies de exposición.

### III. Arquitectura Modular

Cada componente MUST ser independiente, reemplazable y comunicarse vía interfaces bien definidas.

- Componentes MUST ser desplegables independientemente (Docker).
- Comunicación MUST ser vía MCP, APIs REST o colas de mensajes.
- Cada componente MUST tener una sola responsabilidad.
- MUST poder sustituir cualquier componente sin modificar los demás.

**Razón**: La modularidad permite escalar, mantener y evolucionar el sistema sin acoplamiento.

### IV. Calidad y Testing

Toda lógica determinista MUST estar cubierta por tests, incluyendo casos límite.

- MUST existir tests unitarios para: orquestador, tools, embeddings, pipeline RAG, voz.
- Casos límite (servicios caídos, timeouts, datos vacíos, entradas malformadas) MUST estar cubiertos explícitamente.
- El LLM MUST mockearse en tests de integración.
- Cobertura mínima: 80% en código determinista.
- Ningún cambio en lógica crítica MUST integrarse sin su test correspondiente.

**Razón**: Un error silencioso en una regla de orquestación produce fallos indistinguibles a simple vista; los tests son la única garantía sostenible de corrección.

### V. Spec-Driven Development (SDD)

Cada funcionalidad MUST comenzar por una especificación (spec) antes de cualquier implementación.

- Cada feature MUST tener: `spec.md` (qué), `plan.md` (cómo), `tasks.md` (quién/cuándo).
- Cada spec MUST incluir: User Stories con Acceptance Scenarios, Edge Cases, Independent Tests, Functional Requirements, Success Criteria.
- Las especificaciones MUST活着 en `specs/` organizadas por número.
- El ciclo de vida es: Spec → Plan → Tasks → Implement → Review.
- Toda spec MUST pasar el Constitution Check antes de ser implementada.

**Razón**: El SDD garantiza que cada línea de código responde a un requisito explícito, trazable y testeable.

---

## Restricciones Adicionales (Arquitectura y Datos)

- El sistema MUST estructurarse en capas separadas: (1) motor determinista (`src/core/`), (2) capa de voz (`voice/`), (3) interfaz web (`webui/`), (4) infraestructura (`docker/`).
- El LLM MUST consumirse vía opencode-go (deepseek-v4-flash-free) por defecto, configurable en `opencode.json`.
- La memoria MUST combinar grafos (Neo4j) y vectores (Qdrant) con fallback a memoria.
- Los secretos MUST cargarse desde variables de entorno, nunca desde archivos en el repo.

---

## Flujo de Trabajo y Puertas de Calidad

1. **Constitution Check**: Toda spec MUST verificar cumplimiento de estos 5 principios antes de pasar a planificación.
2. **Plan Review**: El plan MUST ser revisado contra la spec antes de generar tasks.
3. **Test-First**: Los tests MUST escribirse antes de la implementación y deben fallar inicialmente.
4. **Implementation Gate**: Implementación MUST pasar todos los tests existentes.
5. **Review Gate**: Cierre de feature MUST incluir checklist de verificación.

---

## Gobernanza

Esta Constitución MUST tener precedencia sobre cualquier otra práctica, convención o preferencia técnica del proyecto.

**Cómo se versiona**:
- **MAJOR**: eliminaciones o redefiniciones incompatibles de principios.
- **MINOR**: adición de un principio nuevo o ampliación material.
- **PATCH**: aclaraciones, correcciones de redacción.

Toda enmienda MUST actualizar la versión, la fecha y revisar la consistencia de las plantillas dependientes.

---

*Esta Constitución es vinculante para todo el desarrollo de JARVIS.*
