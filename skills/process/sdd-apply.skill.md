# SDD Apply

**Parent OS**: Agent OS
**Tier**: 2
**Description**: Ejecuta tareas de implementación siguiendo el plan y tasks definidos

## Rules
1. Una tarea a la vez — no paralelizar
2. Verificar cada tarea inmediatamente después de ejecutarla
3. Si una tarea falla: detenerse, diagnosticar, corregir, continuar
4. No pasar a la siguiente tarea sin verificar la anterior
5. Commits atómicos por fase

## Dependencies
- `skills/process/sdd-design.skill.md` (plan y tasks deben existir primero)

## References
- `docs/PROTOCOLO.md` — 7 mandamientos
