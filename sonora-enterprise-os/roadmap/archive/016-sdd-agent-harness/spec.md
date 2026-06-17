# Feature Specification: SDD Agent Harness

**Feature**: 016-sdd-agent-harness
**Created**: 2026-06-10
**Status**: Active
**Input**: Implementar un marco de desarrollo basado en Spec-Driven Development (SDD) con registro de habilidades, memoria contextual, pipeline de fases y guardas de calidad.

---

## Objetivo

Crear un sistema de orquestación de agentes que asegure el cumplimiento estricto del ciclo SDD (Especificación → Planificación → Tareas → Implementación → Verificación → Archivado) mediante:
- Registro de habilidades indexado (JSON)
- Motor de memoria contextual (Engram) para reuso de soluciones
- Pipeline de subagentes especializados por fase
- Guardas de calidad obligatorias (constitución, checklist, TDD)

---

## Requisitos Funcionales

1. **Registro de Habilidades**  
   - Mantener un índice JSON de todas las habilidades disponibles (skills, MCP tools, agentes)
   - Permitir búsquedas eficientes por nombre, categoría y dependencias
   - Actualizarse automáticamente al descubrir nuevas habilidades

2. **Memoria Contextual (Engram)**  
   - Almacenar lecciones aprendidas y patrones exitosos de specs anteriores
   - Recuperar contexto relevante basado en la similitud de problema actual
   - Evitar repetir errores mediante aprendizaje de constraints violados

3. **Pipeline de Fases**  
   - **Research Agent**: Investiga y genera briefing técnico
   - **Spec Agent**: Convierte briefing en spec.md completa (requisitos, casos de uso)
   - **Design Agent**: Genera plan.md y tasks.md basado en spec
   - **Apply Agent**: Ejecuta tareas utilizando habilidades del registro
   - **Verify Agent**: Valida cumplimiento de constitución, checklist y tests
   - **Archive Agent**: Documenta resultados y actualiza conocimiento

4. **Guardas de Calidad**  
   - **Constitución Check**: Verifica principios fundamentales antes de planificación
   - **Checklist Validation**: Asegura ítems de checklist completados antes de archivado
   - **TDD Gate**: Requiere tests escritos antes de implementación y pasar antes de commit

---

## Casos de Uso

### UC1: Desarrollar Nueva Feature con SDD Estricto
- **Actor**: Desarrollador
- **Flujo**:
  1. Ejecutar `harness init "Nueva Feature"` → Research Agent crea briefing
  2. Spec Agent genera spec.md con requisitos y criterios de aceptación
  3. Design Agent crea plan.md y tasks.md con estimaciones
  4. Apply Agent asigna tareas a habilidades del registro y ejecuta código
  5. Verify Agent corre tests y valida checklist antes de permitir commit
  6. Archive Agent guarda lecciones en Engram y actualiza documentación

### UC2: Mantener Cumplimiento de Constitución
- **Actor**: Sistema Automático
- **Flujo**:
  1. En cada commit, Verifier revisa principios de constitución
  2. Si violación detectada, bloquea operación y notifica al desarrollador
  3. Solo permite avance tras corrección y re-verificación

### UC3: Reutilizar Soluciones Conocidas
- **Actor**: Research Agent
- **Flujo**:
  1. Al investigar una problemática, consulta Engram por soluciones similares
  2. Recupera patrones exitosos y evita enfoques fallidos previamente documentados
  3. Enriquece el briefing con lecciones aprendidas

---

## Criterios de Éxito

- [ ] 100% de specs cumplen con estructura SDD (spec.md, plan.md, tasks.md, checklist.md, data-model.md, contracts/)
- [ ] Motor de Engram reduce tiempo de investigación en 40% mediante reuso de contexto
- [ ] Guardas de calidad previenen 95% de errores estructurales (checklist vacía, tests faltantes)
- [ ] Registro de habilidades permite discovery de capacidades en <100ms
- [ ] Pipeline de fases asegura que ningún commit salte verificaciones obligatorias
- [ ] Documentación técnica actualizada refleja cambios en arquitectura de agentes

---

## Restricciones

- **Separación de Responsabilidades**: Lógica de orquestación debe ser determinista y testeable
- **Privacidad**: Conocimiento almacenado en Engram no debe contener datos sensibles sin cifrado
- **Arquitectura Modular**: Cada componente (registro, engram, harness) debe ser reemplazable independientemente
- **Calidad**: Todo código del harness debe tener >80% de cobertura de tests unitarios
- **Documentación**: Cada cambio debe actualizar spec.md y plan.md correspondientes

---

## Métricas de Éxito

| Métrica | Objetivo | Medición |
|---------|----------|----------|
| Tiempo de Investigación | Reducir 40% | Comparación de tiempo promedio antes/después Engram |
| Cumplimiento SDD | 100% | Porcentaje de specs con todos los archivos requeridos |
| Errores Estructurales | <5% | Número de PRs bloqueados por verify.py / total PRs |
| Latencia de Registro | <100ms | Tiempo promedio de búsqueda en registry.json |
| Coverage de Tests | >80% | Promedio de cobertura en código del harness |

---

## Arquitectura Propuesta

```
┌─────────────────┐
│   Skill Registry│◄──────────────┐
│  (config/registry.json)          │
└─────────────────┘               │
         ▲                         │
         │                         │
┌─────────────────┐   ┌────────────────────┐
│    Engram       │   │   Harness Core     │
│ (src/core/engram)│   │ (src/core/harness)│
└─────────────────┘   └────────┬───────────┘
         ▲                      │
         │                      ▼
┌─────────────────┐   ┌────────────────────┐
│ Research Agent  │   │ Spec Agent         │
│ (agents/research)│   │ (agents/spec)      │
└─────────────────┘   └────────────────────┘
         ▲                      ▲
         │                      │
┌─────────────────┐   ┌────────────────────┐
│ Design Agent    │   │ Apply Agent        │
│ (agents/design) │   │ (agents/apply)     │
└─────────────────┘   └────────────────────┘
         ▲                      │
         │                      ▼
┌─────────────────┐   ┌────────────────────┐
│ Verify Agent    │   │ Archive Agent      │
│ (agents/verify) │   │ (agents/archive)   │
└─────────────────┘   └────────────────────┘
```

---

## Plan de Implementación

### Fase 1: Infraestructura Base
- [ ] Crear `config/registry.json` con habilidades actuales
- [ ] Implementar `src/core/engram.py` con almacenamiento SQLite
- [ ] Definir interfaces de agentes en `src/core/agents/agent_base.py`

### Fase 2: Pipeline de Fases
- [ ] Implementar agentes especializados (Research, Spec, Design, Apply, Verify, Archive)
- [ ] Crear orquestador principal en `src/core/harness.py`
- [ ] Integrar con AgentOrchestrator existente

### Fase 3: Guardas de Calidad
- [ ] Actualizar `src/core/verify.py` con checks de constitución y checklist
- [ ] Implementar TDD gate en pre-commit hook
- [ ] Configurar CI/CD para ejecutar verificaciones automáticas

### Fase 4: Validación y Documentación
- [ ] Crear spec 016 con documentación completa
- [ ] Actualizar INVENTARIO-FINAL.md con evidencia de cumplimiento
- [ ] Ejecutar suite completa de tests (330+)

---

## Dependencias

- **Internas**: AgentOrchestrator existente, MCP skills, Neo4j/Qdrant stores
- **Externas**: SQLite (para Engram), JSON schema validation

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Sobrecarga de contexto | Media | Alto | Limitar tamaño de Engram y usar indexing |
| Resistencia al cambio | Baja | Medio | Capacitación gradual y beneficios demostrables |
| Incompatibilidad con skills existentes | Baja | Alto | Adapter pattern para convertir skills a formato registry |
| Overhead de verificación | Baja | Bajo | Cachear resultados de verificaciones costosas |

---

## Conclusión

El SDD Agent Harness transforma el desarrollo de JARVIS de un enfoque ad-hoc a un proceso de ingeniería rigurosa. Al imponer fases obligatorias, memoria contextual y guardas de calidad, asegura que cada línea de código responda a un requisito explícito, sea testeable y aporte valor verificable. Este marco no solo mejora la calidad del producto, sino que acelera el desarrollo mediante el reuso inteligente de soluciones previamente validadas.

---
**Spec**: spec.md
**Plan**: plan.md (pendiente)
**Tasks**: tasks.md (pendiente)
**Checklist**: checklist.md (pendiente)
**Research**: research.md (este documento)
**Data Model**: data-model.md (pendiente)
**Contracts**: contracts/README.md (pendiente)