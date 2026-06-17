---
name: keyword-matcher
description: "Match user intent by checking if any keywords appear in task text. Use when you need to route tasks by keyword detection."
---

# keyword-matcher

Detecta si alguna palabra clave aparece en el texto de una tarea para decidir qué agente o ruta ejecutar.

## Patrón

```python
def match_keywords(task: str, keywords: list[str]) -> bool:
    task_lower = task.lower()
    return any(kw in task_lower for kw in keywords)
```

## Uso

```python
from src.core.agents.agent_base import match_keywords

if match_keywords(task, ["instalar", "paquete", "apt"]):
    return "package_agent"
```

La función convierte el texto a minúsculas y verifica si al menos un keyword coincide.

## Referencia

`src/core/agents/agent_base.py` — función `match_keywords()`.
