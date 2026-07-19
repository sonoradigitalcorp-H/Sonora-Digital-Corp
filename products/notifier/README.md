# Sonora Notifier — Motor de Notificaciones Multicanal

## ¿Qué hace?
Escucha el bus de eventos de Sonora OS y entrega notificaciones en
tiempo real via WhatsApp, Telegram o Email según reglas configurables.

## Canales
| Canal | Driver | Configuración |
|-------|--------|---------------|
| WhatsApp | wacli_mcp | Autenticación pre-existente |
| Telegram | python-telegram-bot | `TELEGRAM_BOT_TOKEN` env |
| Email | SMTP | `SMTP_HOST`, `SMTP_PORT`, `SMTP_FROM` env |

## Reglas
Cada regla define:
- `event_type`: tipo de evento que la activa (soporta wildcard `*`)
- `channel`: whatsapp, telegram, email
- `template`: mensaje con variables `{{var}}`
- `recipients`: destinatarios (teléfono, chat_id o email)
- `enabled`: activar/desactivar

## Uso

```bash
# Iniciar API
NOTIFIER_PORT=6200 python3 -m products.notifier.main

# Iniciar worker de notificaciones
TELEGRAM_BOT_TOKEN=xxx python3 -m products.notifier.core

# Probar reglas una vez
python3 -m products.notifier.core --once
```

## API
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/notifier/rules` | Listar reglas |
| POST | `/notifier/rules` | Crear regla |
| DELETE | `/notifier/rules/{id}` | Eliminar regla |
| GET | `/notifier/log` | Historial de entregas |
| GET | `/notifier/stats` | Estadísticas |
| GET | `/notifier/health` | Health check |

## Ejemplos

```bash
# Crear regla para responder mensajes de WhatsApp por Telegram
curl -X POST http://localhost:6200/notifier/rules \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "whatsapp:message:received",
    "channel": "telegram",
    "template": "📩 {{from}}: {{text}}",
    "recipients": ["123456789"],
    "tenant": "sdc"
  }'

# Ver estado
curl http://localhost:6200/notifier/health
```
