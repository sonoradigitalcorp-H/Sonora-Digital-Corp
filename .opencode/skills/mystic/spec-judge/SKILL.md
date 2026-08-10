# Skill: Spec Judge (SDD de Joaquín Ruiz)

Juez automático de especificaciones siguiendo Spec-Driven Development (SDD) de Joaquín Ruiz. Verifica que una spec cumpla la metodología ANTES de escribir código.

## Cuándo usar
- Antes de crear cualquier componente nuevo (API, módulo, proceso)
- Cuando se presenta una spec para aprobación
- En el ciclo nocturno de automejora (5:30 AM, Ollama VPS, costo $0)
- Con `/idea` o `/validar` para chequear una propuesta contra la constitución

## Referencias del método (fuente: harvis-os CLAUDE.md + .specify/)
- Workflow: `.specify/workflows/sdd.md`
- Plantilla: `.specify/templates/spec.md`
- Constitución: `.specify/memory/constitution.md`

## Los 5 Principios (Constitution Check)
1. **Orquestación Única** — ¿Entra por el orquestador/dispatcher? ¿No hay comunicación directa entre agentes?
2. **Separación Determinista vs LLM** — ¿La lógica crítica es determinista? ¿El LLM solo se usa cuando es necesario?
3. **Local-first** — ¿Los datos permanecen locales? ¿Se prioriza LLM local (Ollama) sobre APIs pagas?
4. **Testing** — ¿Hay tests (TDD)? ¿Cubren casos límite?
5. **Trazabilidad** — ¿Cada decisión se registra? ¿Se puede auditar el flujo?

## Checklist de evaluación (spec → veredicto)

### Secciones requeridas en la spec
- [ ] **ID** (`XXX-nombre`) y versión
- [ ] **Resumen** claro (1 párrafo)
- [ ] **Objetivo** específico y medible
- [ ] **Contexto** (servicios relacionados + dependencias)
- [ ] **Especificación** con inputs/outputs tipados (contrato)
- [ ] **Testing** (tests TDD + casos límite)
- [ ] **Decisión técnica** documentada (razón + alternativas)

### Criterios de aprobación
- Los 5 principios pasan SIN excepción
- No duplica componentes existentes (verificar `01_Core_Platform/` y `.opencode/skills/`)
- Usa modelo local (Ollama) donde aplica — NO depende de OpenRouter con key $0
- Costo de ejecución justificado

## Flujo del juez
1. Leer la spec candidata
2. `architecture-discovery` en paralelo → verificar que NO exista ya
3. Constitution Check → pasar los 5 principios
4. Evaluar contra la plantilla `.specify/templates/spec.md`
5. Emitir veredicto: **APROBADA** / **APROBADA CON CAMBIOS** / **RECHAZADA** + razones

## Veredictos
- **APROBADA** → 5/5 principios, completo, sin duplicados → se puede implementar (TDD)
- **APROBADA CON CAMBIOS** → faltan secciones o hay principios parciales → listar correcciones
- **RECHAZADA** → duplica algo existente, viola constitución, o depende de recursos agotados

## Output esperado
```
Veredicto: APROBADA | APROBADA CON CAMBIOS | RECHAZADA
Constitution Check: [✅/❌] por principio
Secciones faltantes: [...]
Componentes duplicados: [...]
Correcciones requeridas: [...]
```

## Notas
- Juzgar es MAYEUTICA (análisis), no código — costo $0 con Ollama VPS
- Si hay duda de duplicado → `mem_search` + architecture-discovery primero
- La mejor spec es la que NO necesita implementación nueva

## Ver también
- `harvis-os/.specify/workflows/sdd.md` — workflow SDD
- `01_Core_Platform/05_SelfImprovement/` — evaluator (5-dim scoring)
- `auto-mejora` — ciclo nocturno que usa este judge
