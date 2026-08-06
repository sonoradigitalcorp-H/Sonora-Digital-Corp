# Multi-Tenant Bot Factory

## Qué hace
Crea agentes dedicados por bot Telegram con routing inteligente. Soporta múltiples bots manejando un solo webhook.

## Cuándo usar
- Tienes múltiples bots Telegram para diferentes clientes
- Cada bot debe manejar leads de forma aislada
- Necesitas escalar a más clientes sin duplicar código

## Uso rápido

```bash
# 1. Crear webhook
python3 multi_tenant_webhook.py --port 5289 &

# 2. Registrar tenant
python3 tenant_router.py --bot Aztro_tech_bot --tenant aztrotech --owner "César" --client "Aztrotech Hermosillo"

# 3. Configurar webhook en bot (requiere IP pública)
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  -d "url=http://TU_IP:5289/webhook"

# 4. Alternativa: usar bot central @RyE_production_bot
# Los mensajes se enrutan al agente correcto por tenant_registry.json
```

## Estructura de archivos

```
tenant_router.py      # Registry bot → tenant → agente
channel_forwarder.py  # Middleware de enrutamiento
multi_tenant_webhook.py # Webhook HTTP único
```

## Integración con OpenClaw

Los bindings se gestionan vía:
- `openclaw agents add <tenant> --bind telegram`
- `openclaw agents bindings` para ver configuración actual

## Factores críticos

1. **Webhook público**: Sin IP pública o ngrok, los bots no reciben mensajes
2. **Token de bot**: Cada tenant necesita token único de @BotFather
3. **Tenant isolation**: Cada agente tiene memoria aislada en Engram/Qdrant

## Casos de uso típicos

- Agencia con múltiples clientes (restaurantes, clínicas, etc.)
- Empresas con sucursales separadas
- MVP testing con múltiples bots de prueba