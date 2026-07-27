# speckit.constitution

**Description**: Fija las reglas actuales del proyecto en `.specify/memory/constitution.md`.

**Usage**: `/speckit.constitution`

**Prompt**:
```
Eres un analista de proyectos. Tu tarea es fotografiar las reglas actuales de este proyecto y escribirlas en `.specify/memory/constitution.md`.

Pasos:
1. Lee `kernel/` (todos los YAML/MD) para reglas explícitas
2. Lee `AGENTS.md`, `CLAUDE.md`, `.specify/memory/context.md` para reglas implícitas
3. Extrae patrones de `process/active/SPEC-*.md`, `process/active/plan-*.md`, `process/active/tasks-*.md`
4. Lee `skills/index.yaml` para capacidades y agentes
5. Funde todo en `constitution.md` con 7 niveles:
   - N1: Propósito — PRIMARY DIRECTIVE, Truth Hierarchy
   - N2: Negocio — Revenue Gate, Anti-Fantasy Filter
   - N3: Metodología — Discovery, SDD, ADR, DDD, BDD, ATDD, TDD
   - N4: Ejecución — Context Governance, Agent Harness, Skill Registry
   - N5: Técnico — Separación LLM, Privacidad, Modularidad
   - N6: Gobernanza — Security, Observability, Quality Gates
   - N7: Ciclo SDD — Revenue → Discovery → Spec → BDD → ADR → Plan → Tasks → Code → Verify → Delivery → Archive
6. Actualiza `.specify/memory/context.md` con los specs activos encontrados

Output: `.specify/memory/constitution.md` actualizado + `.specify/memory/context.md`
```
