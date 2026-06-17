from typing import Any, Dict

from src.core.agents.agent_base import AgentBase, success_response, error_response


class SpecAgent(AgentBase):
    name = "spec"
    description = "Genera especificaciones SDD completas a partir de briefings"
    timeout = 60

    async def run(self, task: str, context: dict = None) -> Dict[str, Any]:
        self.log.info(f"Spec generation: {task[:100]}...")

        # Extract briefing from context
        briefing = context.get("research_result", {}).get("synthesis", "")
        if not briefing:
            return error_response(
                self.name, task, "No research briefing found in context"
            )

        # Generate spec structure
        spec_content = f"""# Feature Specification: {task}

**Feature**: {task.replace(' ', '-').lower()}
**Created**: 2026-06-10
**Status**: Active
**Input**: {task}

---

## Objetivo

{briefing[:500]}

---

## Requisitos Funcionales

1. **Requisito 1**
   - Descripción basada en el briefing
   - Criterios de aceptación

2. **Requisito 2**
   - Descripción
   - Criterios

---

## Casos de Uso

### UC1: Caso principal
- **Actor**: Usuario
- **Flujo**: Descripción del flujo principal

---

## Criterios de Éxito

- [ ] Criterio 1
- [ ] Criterio 2
- [ ] Criterio 3

---

## Restricciones

- Restricción 1
- Restricción 2

---

## Métricas de Éxito

| Métrica | Objetivo | Medición |
|---------|----------|----------|
| Métrica 1 | 100% | Método de medición |
"""

        return success_response(
            self.name,
            task,
            action="generate_spec",
            spec_content=spec_content,
            sections=[
                "objetivo",
                "requisitos",
                "casos_uso",
                "criterios",
                "restricciones",
                "metricas",
            ],
        )
