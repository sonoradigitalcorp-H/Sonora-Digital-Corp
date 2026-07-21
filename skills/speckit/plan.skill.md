# speckit.plan

**Description**: Crea plan de implementación desde la SPEC.

**Usage**: `/speckit.plan <spec-id>`

**Steps**:
1. Lee SPEC.md de `process/active/`
2. Evalúa complejidad técnica
3. Crea `process/active/plan-<spec-id>.md`
4. Define estructura de proyecto, dependencias, fases
5. Incluye Constitution Check

**Output**: `process/active/plan-<id>.md` + `process/active/tasks-<id>.md`
