# Twilio Voice Bridge — Configuración

## Prerequisitos

1. Cuenta de Twilio (https://twilio.com) — crédito inicial ~$20
2. Número telefónico comprado en Twilio (~$1/mes)
3. `ffmpeg` instalado en el VPS (conversión de audio)

## Instalación

```bash
cd apps/twilio-voice
pip install -r requirements.txt
```

## Variables de entorno

```bash
export TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxx"
export TWILIO_AUTH_TOKEN="your-auth-token"
export TWILIO_PHONE_NUMBER="+526621072254"
export BASE_URL="https://voice.sonoradigitalcorp.com"
```

## Configuración en Twilio Console

### 1. Número telefónico

```
Twilio Console → Phone Numbers → Manage → Buy a Number
  · México (+52) disponible
  · Seleccionar número con capacidad de voz
```

### 2. Webhook para llamadas entrantes

```
Twilio Console → Phone Numbers → Configure → Voice Configuration

  WHEN A CALL COMES IN: Webhook
    URL: https://voice.sonoradigitalcorp.com/twilio/incoming
    METHOD: POST
```

### 3. Webhook para llamadas salientes

```
No requiere configuración en Twilio.
Se usa la API REST de Twilio para iniciar llamadas.
```

## Iniciar el servicio

```bash
# Local (prueba)
python3 -m apps.twilio_voice.server

# Producción (VPS)
screen -S twilio-voice
python3 -m apps.twilio_voice.server

# O systemd (recomendado)
sudo cp infra/systemd/sdc-twilio-voice.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now sdc-twilio-voice
```

## Probar llamada saliente

```bash
curl -X POST http://localhost:8700/twilio/call/outbound \
  -H "Content-Type: application/json" \
  -d '{
    "to": "+526621072254",
    "agent": "sales-hunter",
    "lead_name": "Juan Pérez",
    "context": "Seguimiento de propuesta de agente IA"
  }'
```

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | /twilio/incoming | Webhook para llamadas entrantes |
| POST | /twilio/call/outbound | Iniciar llamada saliente |
| POST | /twilio/outbound-twiml | TwiML para llamadas salientes |
| WS | /twilio/media-stream/{call_sid} | Streaming bidireccional de audio |
| POST | /twilio/status | Status callback de Twilio |
| GET | /twilio/calls | Listar llamadas activas |
| GET | /twilio/calls/{call_sid} | Detalle de llamada |
| GET | /twilio/health | Health check |

## Costos (Twilio)

| Concepto | Costo |
|----------|-------|
| Número telefónico | $1/mes |
| Minuto de llamada (entrante) | $0.013/min MX |
| Minuto de llamada (saliente) | $0.013/min MX |
| Streaming Media Streams | $0.002/min |
| Kokoro TTS | $0 (local) |
| Whisper STT | $0 (local) |
| deepseek (por llamada ~$0.001) | $0.001/llamada |

**Costo por llamada de 10 min:** ~$0.15 (Twilio) + $0.001 (deepseek) = **~$0.151**
