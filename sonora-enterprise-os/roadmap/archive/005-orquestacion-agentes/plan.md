# Implementation Plan: Orquestación de Agentes

**Spec**: [spec.md](./spec.md)

---

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: Ninguna externa (usa `src/core/tools.py`, `src/core/neo4j_store.py`, `voice/`)
**Architecture**: Singleton AgentOrchestrator con registro de agentes, routing por regex word-boundary
**Testing**: pytest con tests de routing y ejecución

## Constitution Check

| Principio | Cómo lo cumple |
|-----------|---------------|
| Separación de responsabilidades | Cada agente es un módulo independiente con una responsabilidad |
| LLM no decide, solo sugiere | Routing es determinista por keywords, no por LLM |
| Arquitectura modular | Agentes registrables, orquestador desacoplado |
| Calidad y testing | Tests de routing para 17+ casos parametrizados |

## Implementación

### Archivos existentes

| Archivo | Propósito |
|---------|-----------|
| `src/core/orchestrator.py` | AgentBase + 7 agentes + AgentOrchestrator + routing + execute |
| `tests/unit/test_orchestrator.py` | 30 tests: routing, execute, parallel, singleton |

### Pendiente

| Tarea | Prioridad |
|-------|-----------|
| `test_agents.py` — tests unitarios para los 5 nuevos agentes | P1 |
| Pasar datos de contexto entre agentes (ej: ResearchAgent → CodeAgent) | P2 |

## Archivos del spec

```
specs.new/005-orquestacion-agentes/
├── spec.md
├── plan.md
└── tasks.md
```
