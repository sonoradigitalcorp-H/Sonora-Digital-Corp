# Implementation Plan: SDD Agent Harness

**Spec**: [spec.md](./spec.md)

---

## Technical Context

**Language/Version**: Python 3.10+, Go (opencode-go)
**Primary Dependencies**: sqlite3, json-schema, mcp, neo4j, qdrant-client
**Storage**: Registry JSON + SQLite (Engram), Neo4j + Qdrant stores
**Testing**: pytest con mocking de SQLite/LLM

## Constitution Check

| Principio | Cómo lo cumple |
|-----------|---------------|
| Separación de responsabilidades | Harness = estructura SDD, Agentes = lógica determinista, LLM = generación de respuestas |
| Privacidad y control | Datos sensibles en variables de entorno, Engram cifrado si necesario |
| Arquitectura modular | Cada agente (Research/Spec/Design/Apply/Verify/Archive) importable separadamente |
| Calidad y testing | Tests unitarios para cada agente, coverage >80% |
| Spec-Driven Development | Harness implementa ciclo SDD completo con gates obligatorios |

## Implementation

### Phase 1: Registry & Engram (Weeks 1-2)
- [ ] Crear `config/registry.json` con habilidades actuales
- [ ] Implementar `src/core/engram.py` con SQLite + FTS5
- [ ] Añadir skill registry index endpoint

### Phase 2: Harness Core (Weeks 2-3)
- [ ] Crear `src/core/harness.py` con fases Research → Apply → Verify
- [ ] Implementar agentes especializados en `src/core/agents/`
- [ ] Integrar con AgentOrchestrator existente

### Phase 3: Quality Gates (Weeks 3-4)
- [ ] Actualizar `src/core/verify.py` con checks de constitución
- [ ] Implementar pre-commit hook con TDD gate
- [ ] Configurar GitHub Actions para verificación automática

## Files Structure

```
specs/016-sdd-agent-harness/
├── spec.md           # Este archivo
├── plan.md           # Este archivo
├── tasks.md          # Tareas
├── checklist.md      # Checklist de implementación
└── contracts/        # Contratos de APIs
    └── harness-api.json
```

## Success Criteria

- 100% de specs cumplen con estructura SDD
- Engram reduce tiempo de investigación 40%
- Guardas de calidad previenen errores estructurales
- 330+ tests pasando sin regresiones