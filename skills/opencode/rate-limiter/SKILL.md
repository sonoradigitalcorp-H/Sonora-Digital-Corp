---
name: rate-limiter
description: "Rate-limit tool calls per key with configurable window. Use for tools that hit external APIs."
---

# rate-limiter

Limita la frecuencia de llamadas a herramientas por clave configurable para evitar abusos en APIs externas.

## Patrón

```python
from src.core.tools.executors import rate_limit

@rate_limit(key="github_api", max_calls=10, window_sec=60)
def call_github_api(url: str) -> dict:
    # llamada a la API
    pass
```

## Uso

```python
from src.core.tools.executors import rate_limit

# Permite 5 llamadas cada 30 segundos
@rate_limit(key="slack_api", max_calls=5, window_sec=30)
def send_slack_message(msg: str):
    ...
```

Si se excede el límite, la herramienta espera hasta que se reabra la ventana o lanza una excepción.

## Referencia

`src/core/tools/executors.py` — decorador `rate_limit()`.
