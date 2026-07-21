# speckit.implement

**Description**: Ejecuta tareas de implementación una por una.

**Usage**: `/speckit.implement <spec-id> [task-id]`

**Prompt**:
```
Eres un desarrollador implementando la SPEC {spec-id}.

Pasos:
1. Lee `process/active/tasks-{spec-id}.md`
2. Para cada tarea pendiente (no marcada como [x]):
   a. Lee `.specify/memory/constitution.md` — verifica invariantes aplicables
   b. Lee `specs/capabilities/*/spec.md` si la tarea afecta una capacidad existente
   c. Implementa el código
   d. Corre `pytest -q tests/` para verificar que no se rompió nada
   e. Si la tarea incluye tests, escríbelos ANTES del código (TDD)
   f. Marca la tarea como [x] completada
   g. Commit con mensaje: "{spec-id}: {task description}"
3. Si se especifica un task-id, implementa solo esa tarea
4. Al terminar todas las tareas: corre `make test-all` para verificación final

Gate: Cada implementación debe pasar Constitution Check antes de proseguir.
```
