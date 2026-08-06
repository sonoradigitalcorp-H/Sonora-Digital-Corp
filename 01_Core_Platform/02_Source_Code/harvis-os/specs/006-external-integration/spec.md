# Spec 006: External Integration

**ID**: 006-external-integration
**Version**: 1.0.0
**Date**: 2026-08-04
**Author**: Luis Daniel Guerrero Enciso

## Resumen

Integración de Harvis OS con servicios externos: Ollama (LLM), Telegram Bot, y OpenClaw Gateway.

## Objetivo

Conectar Harvis OS con la infraestructura existente para:
- Procesar lenguaje natural con LLMs locales
- Recibir y enviar mensajes via Telegram
- Integrar con OpenClaw para orquestación

## Contexto

### Servicios Existentes (VPS 149.56.46.173)

| Servicio | Puerto | Estado |
|----------|--------|--------|
| PostgreSQL | 5432 | ✅ Activo |
| Redis | 6379 | ✅ Activo |
| Neo4j | 7474/7687 | ✅ Activo |
| Qdrant | 6333/6334 | ✅ Activo |
| MCP Server | 8000 | ✅ Activo |
| n8n | 5678 | ✅ Activo |
| Telegram Bot | 3003 | ✅ Activo |
| Ollama | 11434 | ✅ Activo |

### Configuración Actual

```yaml
ollama:
  base_url: "http://localhost:11434"
  model: "qwen3:4b"
  system_prompt: "Eres HERMES, asistente de IA de Sonora Digital Corp."

telegram:
  bot_token: "${ABE_TELEGRAM_TOKEN}"
  chat_id: "${ABE_TELEGRAM_CHAT}"

openclaw:
  gateway_url: "http://localhost:18789"
```

## Especificación

### Ollama Connector

```python
class OllamaConnector:
    """Conector para Ollama LLM."""
    
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url
        self.model = model
    
    async def chat(self, messages: list[dict], options: dict = None) -> str:
        """Envía mensajes y obtiene respuesta."""
        pass
    
    async def embedding(self, text: str) -> list[float]:
        """Obtiene embedding de texto."""
        pass
    
    def health_check(self) -> dict:
        """Verifica salud de Ollama."""
        pass
```

### Telegram Connector

```python
class TelegramConnector:
    """Conector para Telegram Bot."""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.bot = None
    
    async def send_message(self, chat_id: str, text: str) -> bool:
        """Envía mensaje a Telegram."""
        pass
    
    async def send_voice(self, chat_id: str, audio_path: str) -> bool:
        """Envía nota de voz."""
        pass
    
    def on_message(self, handler: Callable):
        """Registra handler para mensajes entrantes."""
        pass
```

### OpenClaw Connector

```python
class OpenClawConnector:
    """Conector para OpenClaw Gateway."""
    
    def __init__(self, gateway_url: str):
        self.gateway_url = gateway_url
    
    async def send_task(self, task: dict) -> dict:
        """Envía tarea a OpenClaw."""
        pass
    
    async def get_status(self) -> dict:
        """Obtiene estado del gateway."""
        pass
```

## Eventos

### LLM Events

```json
{
  "type": "llm.request",
  "payload": {
    "model": "qwen3:4b",
    "messages": [...],
    "tenant": "sdc-core"
  }
}

{
  "type": "llm.response",
  "payload": {
    "model": "qwen3:4b",
    "reply": "...",
    "tokens_used": 150,
    "duration_ms": 1200
  }
}
```

### Telegram Events

```json
{
  "type": "telegram.message.received",
  "payload": {
    "chat_id": "123456",
    "user_id": "789",
    "text": "Hola"
  }
}

{
  "type": "telegram.message.sent",
  "payload": {
    "chat_id": "123456",
    "text": "Respuesta"
  }
}
```

## Testing

### Casos de Prueba

| ID | Descripción | Input | Output Esperado |
|----|-------------|-------|-----------------|
| TC-001 | Ollama chat | Mensaje | Respuesta del LLM |
| TC-002 | Ollama health | Ping | Status OK |
| TC-003 | Telegram send | Mensaje | Enviado exitosamente |
| TC-004 | OpenClaw status | Ping | Gateway activo |

### Casos Límite

- Ollama no disponible → fallback a OpenRouter
- Telegram API error → retry con backoff
- OpenClaw timeout → cola de mensajes

## Constitution Check

### Principio I: Orquestación Única
- [x] Conectores son infraestructura, no punto de entrada
- [x] Dispatcher usa conectores como dependencia

### Principio II: Separación Determinista vs LLM
- [x] Conectores solo transportan, no deciden
- [x] Lógica de routing sigue siendo determinista

### Principio III: Local-first
- [x] Ollama es local
- [x] Datos no salen del sistema

### Principio IV: Testing
- [x] Tests de integración definidos
- [x] Mocks para servicios externos

### Principio V: Trazabilidad
- [x] Cada llamada al LLM se registra
- [x] Mensajes de Telegram se loguean

## Cambios

| Versión | Fecha | Autor | Cambio |
|---------|-------|-------|--------|
| 1.0.0 | 2026-08-04 | Luis Daniel Guerrero Enciso | Versión inicial |
