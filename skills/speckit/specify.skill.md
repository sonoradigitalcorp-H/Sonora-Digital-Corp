# speckit.specify

**Description**: Crea una SPEC para una nueva funcionalidad en `process/active/`.

**Usage**: `/speckit.specify <feature-title>`

**Prompt**:
```
Eres un especificador técnico. Crea una SPEC completa para: {feature-title}

Pasos:
1. Lee `.specify/templates/spec-template.md` para el formato
2. Lee `.specify/memory/constitution.md` para reglas aplicables
3. Crea `process/active/SPEC-{YYYYMMDD}-{NNN}-{slug}.md`
4. La SPEC debe incluir:
   - User stories priorizadas (P1, P2, P3) con escenarios Given/When/Then
   - Criterios de éxito medibles
   - Requerimientos funcionales
   - Edge cases
   - Constitution Check
5. Actualiza `.specify/memory/context.md` con el nuevo spec

Template: `.specify/templates/spec-template.md`
```
