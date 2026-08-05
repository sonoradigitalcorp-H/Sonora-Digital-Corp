# Security Vault - Sonora Digital Corp

## Esquema de Secretos

Los secretos se almacenan en este directorio siguiendo este patrón:

```
Vault/
├── tenants/
│   ├── aztrotech/
│   │   ├── .env.production       ← API keys, tokens
│   │   ├── whatsapp.key          ← Credenciales WhatsApp
│   │   └── booking_calendar.key  ← Credenciales calendario
│   ├── abe_music_group/
│   │   └── ...
├── infrastructure/
│   ├── engram.key                ← Master key Engram
│   └── openclaw.token            ← Token gateway
├── templates/
│   └── .env.template             ← Template para nuevos tenants
└── .gitkeep
```

## Cómo Acceder a un Secreto (SDK)

```python
from sdc_sdk import SDC_Client
client = SDC_Client("Aztrotech")
token = client.get_secret("whatsapp")  # Lee desde Vault/tenants/aztrotech/
```

## Política de Rotación
- Tokens: 90 días
- Keys: 365 días
- Master keys: Anual (requiere operación manual)

## Auditoría
- Todos los accesos a secretos se registran vía telemetry.py
- Formato: `log_agent_action("Hermes", "Aztrotech", "secret_access", "success", {"secret": "whatsapp"})`
