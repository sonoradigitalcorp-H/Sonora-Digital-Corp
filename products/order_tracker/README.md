# Sonora Order Tracker — Rastreador de Entregas

## ¿Qué hace?
Rastrea servicios contratados desde que se solicitan hasta que se entregan.
Cada orden pasa por: `queued → processing → completed → delivered`.

## Estados
| Estado | Significado |
|--------|-------------|
| queued | Orden creada, esperando asignación |
| processing | Agente trabajando en ella |
| completed | Contenido generado, listo para entregar |
| delivered | Entregado al cliente |
| cancelled | Cancelada por el cliente o el sistema |

## API
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/tracker/orders` | Listar órdenes (filtrable) |
| POST | `/tracker/orders` | Crear orden |
| GET | `/tracker/orders/{id}` | Ver orden |
| PUT | `/tracker/orders/{id}` | Actualizar estado |
| POST | `/tracker/orders/{id}/next` | Avanzar al siguiente estado |
| GET | `/tracker/stats` | Estadísticas |
| WS | `/tracker/ws/{id}` | WebSocket para updates en vivo |
| GET | `/tracker/health` | Health check |

## Uso

```bash
# Iniciar tracker
TRACKER_PORT=6300 python3 -m products.order_tracker.main

# Crear orden
curl -X POST http://localhost:6300/tracker/orders \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "ref-abc123",
    "service_type": "video",
    "description": "Talking head 60s",
    "tokens_cost": 25
  }'

# Avanzar estado
curl -X POST http://localhost:6300/tracker/orders/ORD-ABC12345/next

# Ver orden
curl http://localhost:6300/tracker/orders/ORD-ABC12345
```

## Eventos que emite
- `tracker:order:created` — orden nueva
- `tracker:order:processing` — empezó procesamiento
- `tracker:order:completed` — contenido generado
- `tracker:order:delivered` — entregado al cliente
