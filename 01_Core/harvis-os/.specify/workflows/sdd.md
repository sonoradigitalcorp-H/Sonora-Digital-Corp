# Workflow: Spec-Driven Development (SDD)

**Referencia**: Joaquín Ruiz - Del Vibe Coding al Spec-Driven Development

## Flujo de Trabajo

```
┌─────────────────────────────────────────────────────────────┐
│                     SDD WORKFLOW                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. DISCOVERY                                               │
│     ├─ Entender el problema                                 │
│     ├─ Identificar servicios existentes                     │
│     └─ Definir alcance                                      │
│                                                             │
│  2. CONSTITUTION CHECK                                      │
│     ├─ Verificar Principio I (Orquestación Única)           │
│     ├─ Verificar Principio II (Determinista vs LLM)         │
│     ├─ Verificar Principio III (Local-first)                │
│     ├─ Verificar Principio IV (Testing)                     │
│     └─ Verificar Principio V (Trazabilidad)                 │
│                                                             │
│  3. SPEC                                                    │
│     ├─ Definir inputs/outputs                               │
│     ├─ Definir contrato                                     │
│     ├─ Definir testing                                      │
│     └─ Documentar decisión                                  │
│                                                             │
│  4. PLAN                                                    │
│     ├─ Dividir en fases                                     │
│     ├─ Estimar tareas                                       │
│     ├─ Identificar dependencias                             │
│     └─ Definir criterios de éxito                           │
│                                                             │
│  5. TASKS                                                   │
│     ├─ Desglosar tareas                                     │
│     ├─ Priorizar (P0, P1, P2)                               │
│     ├─ Asignar estimaciones                                 │
│     └─ Definir subtareas                                    │
│                                                             │
│  6. IMPLEMENT                                               │
│     ├─ Escribir tests primero (TDD)                         │
│     ├─ Implementar código                                   │
│     ├─ Verificar tests                                      │
│     └─ Documentar cambios                                   │
│                                                             │
│  7. VALIDATE                                                │
│     ├─ Constitution Check final                             │
│     ├─ Revisión de código                                   │
│     ├─ Verificar métricas                                   │
│     └─ Actualizar documentación                             │
│                                                             │
│  8. RELEASE                                                 │
│     ├─ Tag de versión                                       │
│     ├─ Changelog                                            │
│     ├─ Deploy                                               │
│     └─ Monitoreo                                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Reglas del Flujo

### Regla 1: Nunca saltar fases

Cada fase debe completarse antes de pasar a la siguiente.

### Regla 2: Constitution Check es obligatorio

Antes de CADA implementación, se debe pasar el Constitution Check.

### Regla 3: Specs antes que código

Nunca escribir código sin una spec aprobada.

### Regla 4: Tests antes que implementación

Seguir TDD: test → implement → refactor.

### Regla 5: Documentar decisiones

Cada decisión técnica debe documentarse con razón y alternativas consideradas.

## Plantillas

| Plantilla | Propósito | Ubicación |
|-----------|-----------|-----------|
| spec.md | Especificación de componente | .specify/templates/spec.md |
| plan.md | Plan de implementación | .specify/templates/plan.md |
| tasks.md | Lista de tareas | .specify/templates/tasks.md |

## Ejemplo de Uso

### 1. Discovery

```markdown
## Discovery — Dispatcher

### Problema
El usuario es el cuello de botella porque no existe un punto único de entrada.

### Servicios Existentes
- Telegram Bot (entrada)
- OpenHands (agente)
- OpenCode (agente)
- Hermes (agente)
- Aider (agente)

### Alcance
- Crear Dispatcher que reciba inputs
- Clasificar tareas
- Routing a agentes apropiados
```

### 2. Constitution Check

```markdown
## Constitution Check — Dispatcher

### Principio I: Orquestación Única
- [x] Entra por Dispatcher
- [x] No hay comunicación directa entre agentes

### Principio II: Separación Determinista vs LLM
- [x] Routing es determinista (reglas)
- [x] LLM solo para ambigüedad

### Principio III: Local-first
- [x] Datos locales
- [x] LLM local prioridad

### Principio IV: Testing
- [x] Tests de routing definidos

### Principio V: Trazabilidad
- [x] Cada decisión se registra
```

### 3. Spec

```markdown
## Spec 002: Dispatcher

### Resumen
Punto único de entrada que clasifica y rutea tareas.

### Inputs
- Telegram message
- Web request
- CLI command

### Outputs
- TaskRequest (tarea clasificada)

### Contrato
- events_consume: telegram.message, web.request
- events_publish: task.created
```

## Métricas del Workflow

| Métrica | Target |
|---------|--------|
| Tiempo de Discovery | < 1 hora |
| Tiempo de Spec | < 2 horas |
| Tiempo de Plan | < 1 hora |
| Tiempo de Tasks | < 30 min |
| Constitution Check | 100% antes de implementar |
| Cobertura de tests | > 80% |

## Referencias

- Joaquín Ruiz - Del Vibe Coding al Spec-Driven Development
- GitHub Spec Kit
- SDD Methodology
