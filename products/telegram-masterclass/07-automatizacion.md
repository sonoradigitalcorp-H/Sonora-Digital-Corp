# 7. Automatizacion — n8n + Bots

## Crossposting Automatico
```
Instagram Post → n8n detecta
  → n8n envia a Telegram grupo
  → n8n envia a canal de noticias
  → n8n publica en Twitter
```

## Workflows n8n para Telegram
### 1. Bienvenida Automatica
```
Trigger: Nuevo miembro en grupo
  → Enviar mensaje de bienvenida
  → Enviar link al catalogo
  → Preguntar: "Que genero musical te gusta?"
```

### 2. Recordatorio de Pago
```
Trigger: Pedido creado (via webhook del bot)
  → Wait 24h
  → Si no pagado: recordatorio al cliente
  → Wait 48h
  → Si no pagado: cancelar pedido + notificar admin
```

### 3. Contenido Diario
```
Trigger: Cron 9:00 AM
  → Scrape noticias de musica
  → Resumir con IA
  → Publicar en grupo + canal
```

### 4. Bot ↔ Bot Communication
```
Mensaje del AzRECBot → n8n
  → n8n decide: "venta" o "soporte" o "comunidad"
  → Si "venta": reenviar al admin
  → Si "soporte": responder con FAQ
  → Si "comunidad": publicar en grupo
```

## Como Conectar n8n con Telegram
1. n8n ya corre en: http://localhost:5678
2. Crear webhook en n8n
3. Configurar Telegram bot: 
   - Settings → Group Privacy → Disable (para que lea mensajes)
   - Set Webhook: POST https://tu-dominio.ngrok-free.dev/webhook/telegram
4. El webhook recibe updates → n8n procesa
