---
name: path-extractor
description: "Extract file paths from natural language using regex. Use when a user mentions a file path in their task."
---

# path-extractor

Extrae rutas de archivo mencionadas en lenguaje natural usando una expresión regular.

## Patrón

```python
import re

def extract_file_path(task: str) -> str | None:
    match = re.search(r'[\w/.\-]+\.\w+', task)
    return match.group() if match else None
```

## Uso

```python
from src.core.agents.agent_base import extract_file_path

path = extract_file_path("editar src/main.py para agregar logging")
if path:
    print(f"Archivo detectado: {path}")
```

La regex captura secuencias de caracteres alfanuméricos, barras, puntos y guiones que terminen en una extensión.

## Referencia

`src/core/agents/agent_base.py` — función `extract_file_path()`.
