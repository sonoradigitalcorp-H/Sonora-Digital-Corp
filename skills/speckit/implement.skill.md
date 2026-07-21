# speckit.implement

**Description**: Ejecuta tareas de implementación una por una.

**Usage**: `/speckit.implement <spec-id> [task-id]`

**Steps**:
1. Lee `process/active/tasks-<spec-id>.md`
2. Para cada tarea pendiente:
   - Lee constitución (invariantes)
   - Implementa
   - Corre tests relevantes
   - Commit
3. Marca tarea como completada
4. Al final: `pytest -q` para verificar

**Gate**: Cada implementación debe pasar Constitution Check antes de proseguir.
