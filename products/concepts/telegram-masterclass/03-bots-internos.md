# 3. Bots Internos — Comunicacion Entre Bots

## Arquitectura
Cada bot se conecta a un "router" central en Python que decide si:
- El mensaje es para el bot A → responde
- El mensaje contiene keyword X → reenvia al bot B
- El mensaje es comando /X → ejecuta accion Y

## Como Hacer que los Bots Hablen Entre Si

### Metodo 1: Forwarding via Webhooks
```
Bot A recibe mensaje
  → POST a http://router:3003/forward
  → Router decide: "esto es para Bot B"
  → Router llama sendMessage en Bot B
  → Bot B responde al usuario
```

### Metodo 2: Base de Datos Compartida
```
Bot A escribe en Redis/Neo4j: {"user_id": 123, "intent": "venta"}
Bot B lee de Redis/Neo4j: ¿hay nuevas intenciones?
  → Si, proceso la venta
  → Respondo al usuario
```

### Metodo 3: n8n como Orquestador
```
Telegram Webhook → n8n → [procesa] → Telegram
n8n conecta: Bot A ↔ Bot B ↔ API ↔ Base de datos
```

## Implementacion Actual (SDC)
Nuestro sistema usa un solo proceso Python (`telegram_bot`) que carga **3 bots**:
- default (publico)
- admin (solo admins)
- abraham (personal)

### Comunicacion Interna
```
Usuario → @default_bot
  → default_bot procesa
  → Si es admin: reenvia a admin_bot
  → Si es abraham: reenvia a abraham_bot
  → Todos escriben al mismo grupo/conversacion
```

### Sistema de Roles
| Rol | Acceso | Bot |
|-----|--------|-----|
| Usuario publico | Comandos basicos, ayuda | default |
| Cliente | Catalogo, compras | default + AzREC |
| Admin | Gestion, monitoreo | admin |
| Sistema | Alertas, logs | internal (sin chat) |

## Ejemplo: Bot A habla con Bot B

```python
# Bot A recibe comando /producto
async def producto_handler(update, context):
    # Consulta a Bot B via HTTP
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "http://localhost:8766/query",  # Publisher service
            json={"producto": "gorra-classic"}
        )
        data = resp.json()
    await update.message.reply_text(f"Precio: {data['price']}")
```

## Mini-Juegos Entre Bots
Los bots pueden:
- Jugar trivia musical (pregunta un bot, responde el otro)
- Pasar "el dado" (random entre bots)
- Competencia de chistes
- Status check (un bot pregunta "vivo?" al otro)
