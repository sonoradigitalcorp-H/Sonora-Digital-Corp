# speckit.tasks

**Description**: Genera tareas ordenadas por dependencias desde plan + spec.

**Usage**: `/speckit.tasks <spec-id>`

**Steps**:
1. Lee plan.md + spec.md
2. Aplica `.specify/templates/tasks-template.md`
3. Crea `process/active/tasks-<spec-id>.md`
4. Organiza en fases: Setup → Foundation → US1 → US2 → US3 → Polish

**Output**: `process/active/tasks-<id>.md`
