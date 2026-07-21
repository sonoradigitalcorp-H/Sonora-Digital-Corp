---
name: response-builder
description: "Build consistent success/error responses for agent methods. Use in any agent method that returns a dict."
---

# response-builder

Construye respuestas estandarizadas con formato uniforme para todos los métodos de agente.

## Patrón

```python
def success_response(data: dict, message: str = "") -> dict:
    return {"status": "ok", "data": data, "message": message}

def error_response(error: str, code: int = 400) -> dict:
    return {"status": "error", "error": error, "code": code}
```

## Uso

```python
from src.core.agents.agent_base import success_response, error_response

if result:
    return success_response({"id": result.id}, "Creado exitosamente")
return error_response("No se encontró el recurso", 404)
```

Formato estándar: `{"status": "ok" | "error", "data"?, "message"?, "error"?, "code"?}`.

## Referencia

`src/core/agents/agent_base.py` — funciones `success_response()` y `error_response()`.
