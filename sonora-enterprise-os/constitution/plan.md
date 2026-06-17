# Implementation Plan: Constitución del Proyecto

**Spec**: constitution.md

---

## Technical Context

**Language/Version**: Markdown (documento de gobernanza)
**Primary Dependencies**: None (es un documento de constitución)
**Scope**: Gobernanza y principios del proyecto JARVIS

## Constitution Check

| Principio | Cómo se aplica |
|-----------|---------------|
| Separación de responsabilidades | Esta constitución define la separación entre lógica determinista (Python) y LLM (opencode-go) |
| Privacidad y control | Los datos permanecen locales, solo LLM externo es opencode-go |
| Arquitectura modular | Los componentes son independientes y comunicados vía MCP/APIs |
| Calidad y testing | Todo código determinista debe tener tests >80% cobertura |
| Spec-Driven Development | Cada feature comienza con spec.md → plan.md → tasks.md |

## Implementation Strategy

### Phase 1: Establish Constitution
- [ ] Documentar constitución en formato oficial (constitution.md)
- [ ] Crear templates de spec, plan, tasks, checklist
- [ ] Configurar workflow de revisión de constitución

### Phase 2: Governance Setup
- [ ] Definir proceso de versionado (SemVer)
- [ ] Establecer checklist de constitución para cada spec
- [ ] Crear script de verificación automática

### Phase 3: Integration
- [ ] Integrar constitución con CI/CD
- [ ] Añadir verificación automática en PR checks
- [ ] Documentar en INVENTARIO-FINAL.md

## Files Structure

```
specs/000-constitucion/
├── constitution.md    # Este archivo (spec)
├── plan.md            # Este archivo
├── tasks.md           # Tareas
├── checklist.md       # Checklist de implementación
├── research.md        # Investigación de principios
├── data-model.md      # Modelo de datos (N/A - es gobernanza)
└── contracts/         # Contratos (N/A - es gobernanza)
```

## Success Criteria

- [ ] Constitución formal aprobada y documentada
- [ ] Templates SDD actualizados y validados
- [ ] Workflow de constitución integrado en CI/CD
- [ ] INVENTARIO-FINAL.md actualizado con 100% cumplimiento