# Aztrotech — Credenciales Pendientes

## Google Calendar (para booking automático)
**Estado**: Pendiente
**Qué se necesita**:
1. Crear Service Account en Google Cloud Console
2. Habilitar Google Calendar API
3. Descargar JSON con credenciales
4. Compartir el Calendar con el email del Service Account

**Variables de entorno**:
```
GOOGLE_CALENDAR_CREDS=/ruta/a/credentials.json
GOOGLE_CALENDAR_ID=tu-calendar-id@group.calendar.google.com
```

**Para obtener el Calendar ID**:
1. Abrir Google Calendar
2. Configuración → Calendarios → tu calendario
3. Copiar "ID de calendario"

---

## SMTP (para emails de confirmación)
**Estado**: Pendiente
**Qué se necesita**:
1. Account de Gmail con 2FA activado
2. Generar App Password en https://myaccount.google.com/apppasswords

**Variables de entorno**:
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASS=tu-app-password
FROM_EMAIL=noreply@aztrotech.mx
```

---

## Telegram Canal (para contenido de César)
**Estado**: Pendiente
**Qué se necesita**:
1. Ir a https://my.telegram.org
2. Iniciar sesión con el número de César
3. Crear una aplicación
4. Copiar api_id y api_hash

**Variables de entorno**:
```
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=tu-api-hash
```

---

## WhatsApp (re-autenticación)
**Estado**: Pendiente
**Qué se necesita**:
1. Escanear QR desde el teléfono de César
2. Ejecutar: `bash scripts/reauth-whatsapp.sh`

---

## OpenClaw MCP
**Estado**: Offline
**Puerto**: 18789
**Acción**: Verificar por qué no está corriendo

```bash
# Verificar si el servicio existe
systemctl status sdc-openclaw 2>/dev/null

# Si no existe, revisar cómo iniciar
ls /home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/skills/mcp/gateway/
```

---

## VPS (deploy)
**Estado**: Caído
**IP**: 149.56.46.173
**SSH**: alias `ovh`

**Cuando esté disponible**:
```bash
# Deploy voice assistant
rsync -avz tenants/Aztrotech/web/voice-app/dist/ ovh:/var/www/voice/

# Deploy bot
rsync -avz tenants/Aztrotech/bot/ ovh:/home/ubuntu/sonora-digital-corp/tenants/Aztrotech/bot/
```

---

## Checklist de Activación

- [ ] Google Calendar credentials
- [ ] SMTP credentials  
- [ ] Telegram api_id/api_hash
- [ ] WhatsApp re-auth
- [ ] OpenClaw MCP online
- [ ] VPS deploy
- [ ] Dominio aztrotech.mx/voice
- [ ] Test end-to-end con lead real
