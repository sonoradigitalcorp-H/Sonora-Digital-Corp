# speckit.specify

**Description**: Crea una SPEC para una nueva funcionalidad en `process/active/`.

**Usage**: `/speckit.specify <feature-title>`

**Steps**:
1. Lee `.specify/templates/spec-template.md`
2. Crea `process/active/SPEC-YYYYMMDD-NNN-<slug>.md`
3. Aplica Constitution Check
4. Actualiza `.specify/memory/context.md`

**Output**: `process/active/SPEC-<id>.md` + entrada en `specs/index.yaml`
