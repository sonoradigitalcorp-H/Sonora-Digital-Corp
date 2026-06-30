from typing import Any

from src.core.agents.agent_base import AgentBase, error_response, success_response


class DesignAgent(AgentBase):
    name = "design"
    description = "Genera plan.md y tasks.md a partir de especificaciones"
    timeout = 60

    async def run(self, task: str, context: dict = None) -> dict[str, Any]:
        self.log.info(f"Design phase: {task[:100]}...")

        # Extract spec from context
        spec_content = context.get("spec_result", {}).get("spec_content", "")
        if not spec_content:
            return error_response(self.name, task, "No spec content found in context")

        # Generate plan structure
        plan_content = f"""# Implementation Plan: {task}

**Spec**: [spec.md](./spec.md)

---

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: Basado en requisitos del spec
**Storage**: Según necesidades del feature
**Testing**: pytest con mocking de servicios externos

## Constitution Check

| Principio | Cómo lo cumple |
|-----------|---------------|
| Separación de responsabilidades | Lógica determinista en Python, LLM solo para generación |
| Privacidad y control | Datos locales, sin telemetría externa |
| Arquitectura modular | Componentes independientes y reemplazables |
| Calidad y testing | Tests unitarios e integración con >80% coverage |

## Implementation

### Phase 1: Infraestructura Base
- [ ] Tarea 1 de infraestructura
- [ ] Tarea 2 de infraestructura

### Phase 2: Lógica de Negocio
- [ ] Tarea 1 de lógica
- [ ] Tarea 2 de lógica

### Phase 3: Integración y Testing
- [ ] Tarea 1 de integración
- [ ] Tarea 2 de testing

## Success Criteria

- 100% de requisitos funcionales implementados
- Todos los tests pasando
- Documentación actualizada
"""

        # Generate tasks structure
        tasks_content = f"""# Tasks: {task}

---

## US1 — Caso de uso principal (P1)
- [ ] Implementar componente A
- [ ] Implementar componente B
- [ ] Integrar con sistema existente

## US2 — Caso de uso secundario (P2)
- [ ] Implementar funcionalidad X
- [ ] Implementar funcionalidad Y

---

**Completado**: 0 tareas | **Pendiente**: 5 tareas
"""

        return success_response(
            self.name,
            task,
            action="generate_plan_and_tasks",
            plan_content=plan_content,
            tasks_content=tasks_content,
            phases=["infraestructura", "logica", "integracion"],
        )
