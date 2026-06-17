# JARVIS — Constitución del Proyecto

**Versión**: 2.0.0
**Ratificada**: 2026-06-15
**Última modificación**: 2026-06-15

---

## NIVEL 1: PROPÓSITO

### PRIMARY DIRECTIVE

La razón de ser de este sistema NO es construir tecnología.

La razón de ser es generar valor medible para clientes que produce revenue mediante sistemas de software confiables.

**Jerarquía de prioridad:**
1. Revenue
2. Delivery
3. Retención
4. Eficiencia operacional
5. Escalabilidad
6. Experimentación

Lo demás es secundario. Toda acción debe mover el proyecto hacia revenue, delivery, retención o eficiencia.

### TRUTH HIERARCHY

Orden de autoridad para resolver conflictos:

1. CLIENT REQUEST
2. APPROVED SPEC
3. APPROVED ADR
4. APPROVED TASK
5. TESTS
6. IMPLEMENTATION
7. DOCUMENTATION
8. MEMORY
9. ASSUMPTIONS

La autoridad superior siempre gana. Sin excepciones.

### FINAL RULE

No optimices para sofisticación.
Optimiza para valor entregado al cliente.
Optimiza para confiabilidad.
Optimiza para mantenibilidad.
Optimiza para revenue.

Revenue precede a complejidad. Delivery precede a perfección.

---

## NIVEL 2: NEGOCIO

### REVENUE GATE

Antes de cualquier trabajo, responder:

- ¿Quién paga?
- ¿Por qué pagan?
- ¿Qué problema se resuelve?
- ¿Cómo se mide el valor?
- ¿Cuándo se entrega el valor?
- ¿Qué impacto en revenue existe?

Si estas respuestas no existen: BLOQUEAR IMPLEMENTACIÓN.

### ANTI-FANTASY FILTER

Toda feature debe responder:

- ¿Quién la solicitó?
- ¿Qué problema resuelve?
- ¿Qué revenue genera?
- ¿Qué costo elimina?
- ¿Cómo se mide el éxito?

Si las respuestas no existen: RECHAZAR FEATURE.

### RESEARCH LIMIT

- Máximo research antes de delivery: 20%
- Mínimo delivery effort: 80%
- El sistema debe sesgar hacia entregar valor.

### PRODUCTION CLASSIFICATION

Toda feature debe clasificarse. No puede saltarse etapas:

1. RESEARCH — investigación, sin código
2. PROTOTYPE — prueba de concepto, descartable
3. MVP — mínimo producto viable, usuarios reales
4. PRODUCTION — uso en producción, monitoreado
5. REVENUE — generando ingresos
6. SCALE — escalando a más clientes

### BUSINESS DRIVEN DEVELOPMENT

Antes de especificar, definir:

- Problema del cliente
- Valor para el cliente
- Resultado de negocio esperado
- Impacto en revenue
- Impacto operacional
- Impacto en retención

Si no existe resultado de negocio: RECHAZAR FEATURE.

---

## NIVEL 3: METODOLOGÍA

### DISCOVERY PHASE

Generar DISCOVERY.md antes de cualquier especificación.

Definir:
- Business objective
- Success criteria
- User outcomes
- Failure outcomes
- Constraints
- Dependencies
- Unknowns
- Risks
- Edge cases

**No coding allowed.**

### SPEC DRIVEN DEVELOPMENT (SDD)

Cada funcionalidad MUST comenzar por una especificación antes de cualquier implementación.

- Cada feature MUST tener: `spec.md` (qué), `plan.md` (cómo), `tasks.md` (quién/cuándo)
- Cada spec MUST incluir: User Stories con Acceptance Scenarios, Edge Cases, Independent Tests, Functional Requirements, Success Criteria
- Las especificaciones MUST vivir en `specs/` organizadas por número
- El ciclo de vida integrado es: Revenue Gate → Discovery → Spec → ADR → Plan → Tasks → Implement → Verify → Delivery Gate → Archive
- Toda spec MUST pasar el Constitution Check antes de ser implementada

### ARCHITECTURE DECISION RECORDS

Cualquier decisión que involucre:

- Frameworks
- Bases de datos
- Proveedores de IA
- Autenticación
- Pagos
- Despliegue
- Sistemas de memoria
- Bases de datos vectoriales

REQUIERE ADR. El ADR debe contener:

- Contexto
- Decisión
- Alternativas
- Tradeoffs
- Riesgos
- Rollback
- Aprobación

No implementación antes de aprobación del ADR.

### DOMAIN DRIVEN DESIGN

Separar dominios. Ejemplos:

- CRM
- Commerce
- Artists
- Content
- Events
- Analytics
- Subscriptions
- Support

Nunca crear lógica de negocio monolítica.

### BEHAVIOR DRIVEN DEVELOPMENT

Crear escenarios Given/When/Then:

- Acceptance outcomes
- Business outcomes

### ACCEPTANCE TEST DRIVEN DEVELOPMENT

Definir acceptance tests antes de implementación:

- Business acceptance
- User acceptance
- Operational acceptance
- Security acceptance
- Performance acceptance

### TEST DRIVEN DEVELOPMENT

Los tests existen antes del código. Requerido:

- Unitarios
- Integración
- Contrato
- Regresión
- Seguridad
- Rendimiento

Cobertura mínima: 80%.

---

## NIVEL 4: EJECUCIÓN

### CONTEXT GOVERNANCE

Antes de cada task crear:

- Known Facts
- Unknown Facts
- Assumptions (nunca tratarlas como hechos)
- Dependencies
- Constraints
- Risks

Si las assumptions afectan: payments, security, database, infrastructure, compliance, client data → BLOQUEAR IMPLEMENTACIÓN.

### EXECUTION CONTRACT

Antes de implementación crear:

- Goal
- Scope
- Files allowed
- Files forbidden
- Success criteria
- Rollback plan
- Risk level
- Approval status

El agente NO puede salirse del scope.

### AGENT GOVERNANCE

Los agentes NO:

- Improvisan
- Auto-expanden scope
- Inventan requirements
- Inventan arquitectura
- Inventan APIs
- Crean dependencias sin aprobación

### AGENT HARNESS

Todo agente debe definir:

- Inputs
- Outputs
- Dependencies
- Validation criteria
- Failure conditions
- Recovery actions
- Escalation path

### SKILL REGISTRY

Toda capacidad debe ser un skill reutilizable.

Cada skill contiene:
- Purpose
- When to use
- When not to use
- Inputs
- Outputs
- Examples
- Anti-patterns
- Validation
- Metrics

---

## NIVEL 5: TÉCNICO

### I. Separación de Responsabilidades (Decisión Determinista vs. LLM)

La lógica de orquestación, routing y validación MUST ser 100% determinista, reproducible y testeable.

- El motor de decisión (orquestador, routing de agentes, tools, pipeline RAG) MUST estar implementado como código determinista sin dependencia de modelos generativos.
- El LLM MUST limitarse a generar respuestas y análisis a partir de datos **ya procesados**. El LLM MUST NOT decidir rutas, alterar estados ni ejecutar comandos sin validación determinista.
- La interfaz entre el motor determinista y el LLM MUST ser unidireccional: los datos fluyen hacia el LLM; nada producido por el LLM retroalimenta el estado del sistema sin pasar por validación.

### II. Privacidad y Control Local

Los datos del usuario MUST permanecer en la máquina local y MUST NOT transmitirse a servicios externos sin consentimiento explícito.

- La única conexión externa permitida es la llamada al LLM vía opencode-go/OpenRouter.
- Datos sensibles MUST estar en variables de entorno, nunca en código.
- Sin telemetría ni tracking externo.
- El usuario MUST tener control total sobre qué modelos y servicios se usan.

### III. Arquitectura Modular

Cada componente MUST ser independiente, reemplazable y comunicarse vía interfaces bien definidas.

- Componentes MUST ser desplegables independientemente (Docker).
- Comunicación MUST ser vía MCP, APIs REST o colas de mensajes.
- Cada componente MUST tener una sola responsabilidad.
- MUST poder sustituir cualquier componente sin modificar los demás.

### IV. Calidad y Testing

Toda lógica determinista MUST estar cubierta por tests, incluyendo casos límite.

- MUST existir tests unitarios para: orquestador, tools, embeddings, pipeline RAG, voz.
- Casos límite (servicios caídos, timeouts, datos vacíos, entradas malformadas) MUST estar cubiertos explícitamente.
- El LLM MUST mockearse en tests de integración.
- Cobertura mínima: 80% en código determinista.
- Ningún cambio en lógica crítica MUST integrarse sin su test correspondiente.

---

## NIVEL 6: GOBERNANZA

### SECURITY FIRST

Revisar antes de producción:

- Autenticación
- Autorización
- Secretos
- Pagos
- PII
- Prompt injection
- RAG poisoning
- Supply chain attacks
- Rate limits

No deployment sin security review.

### OBSERVABILITY FIRST

Toda feature define:

- Logs
- Metrics
- Tracing
- Alerts
- Dashboards
- Failure detection

Si una falla no puede detectarse: LA FEATURE ESTÁ INCOMPLETA.

### MEMORY GOVERNANCE

La memoria no es verdad.

Tiers de memoria:
- Working Memory
- Session Memory
- Project Memory
- Repository Memory
- Client Memory
- Business Memory

La memoria puede apoyar decisiones. La memoria NUNCA puede override especificaciones.

### RAG GOVERNANCE

- RAG es retrieval.
- RAG no es memoria.
- RAG no es lógica de negocio.
- RAG solo provee contexto.

Decisiones de negocio requieren fuentes verificadas.

### MCP GOVERNANCE

- MCP es acceso a herramientas.
- MCP no es memoria.
- MCP no es orquestación.
- MCP no es razonamiento.

Toda integración MCP debe definir:
- Purpose
- Permissions
- Risks
- Rate limits
- Failure handling

### REPOSITORY GOVERNANCE

Prohibido sin aprobación:

- Mover carpetas
- Borrar archivos
- Cambiar arquitectura
- Agregar frameworks
- Cambiar dependencias
- Renombrar dominios

Todo cambio estructural requiere ADR.

### QUALITY GATES

Requerido para deployment:

- Build pasa
- Tests pasan
- Cobertura >= 80%
- Lint pasa
- Seguridad pasa
- Documentación actualizada
- Rollback disponible

Si alguno falla: BLOQUEAR DEPLOYMENT.

### DELIVERY GATE

Una feature está completa SOLO cuando:

- El cliente puede usarla
- El cliente recibe valor
- Documentación existe
- Deployment existe
- Monitoreo existe
- Rollback existe

Cualquier otra cosa es trabajo inconcluso.

---

## NIVEL 7: CICLO DE VIDA INTEGRADO

```
┌─────────────────────────────────────────────────────────────┐
│                     CICLO SDD v2                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. REVENUE GATE ─→ 2. DISCOVERY ─→ 3. SPEC               │
│       ↓                              ↓                      │
│  4. ADR GATE ←─── BDD/ATDD GATE ←───┘                      │
│       ↓                                                     │
│  5. PLAN ─→ 6. TASKS ─→ 7. CODE ─→ 8. VERIFY               │
│                                                             │
│  9. DELIVERY GATE ─→ 10. ARCHIVE                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Paso a paso:

1. **REVENUE GATE** — ¿Quién paga? ¿Qué problema? ¿Revenue impact? Si no pasa: BLOCK.
2. **DISCOVERY** — DISCOVERY.md. Business objective, constraints, risks, unknowns.
3. **SPEC** — spec.md con user stories, acceptance scenarios, edge cases, func reqs.
4. **BDD/ATDD GATE** — Escenarios Given/When/Then + acceptance tests definidos.
5. **ADR GATE** — ADR si aplica (frameworks, DB, AI, auth, payments, deploy).
6. **PLAN** — plan.md con archivos, riesgos, estimación.
7. **TASKS** — tasks.md con tareas atómicas.
8. **CODE** — Una task a la vez, tests después de cada una.
9. **VERIFY** — Test suite completa, cobertura, bridges, endpoints.
10. **DELIVERY GATE** — ¿Deployado? ¿Monitoreado? ¿Rollback listo?
11. **ARCHIVE** — Commit con referencias, actualizar DOCUMENTO_DE_ERRORES.

---

## Gobernanza de la Constitución

Esta Constitución MUST tener precedencia sobre cualquier otra práctica, convención o preferencia técnica del proyecto.

**Cómo se versiona:**
- **MAJOR**: eliminaciones o redefiniciones incompatibles de principios.
- **MINOR**: adición de un principio nuevo o ampliación material.
- **PATCH**: aclaraciones, correcciones de redacción.

Toda enmienda MUST actualizar la versión, la fecha y revisar la consistencia de las plantillas dependientes.

---

*Esta Constitución es vinculante para todo el desarrollo de JARVIS.*
