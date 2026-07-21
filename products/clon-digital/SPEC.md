# SPEC — Sistema de Clon Digital Autónomo

## Índice
1. Resumen ejecutivo
2. Arquitectura del sistema
3. Especificación de APIs
4. Modelo de datos
5. Flujos de trabajo
6. Integraciones externas
7. Despliegue
8. Monitoreo
9. Plan de implementación

---

## 1. Resumen Ejecutivo

Sistema SaaS que permite a clientes recibir videos personalizados con su propia imagen y voz generados por IA. El sistema opera de forma autónoma: recibe pedidos, entrena modelos, genera contenido, obtiene aprobación y entrega — todo orquestado por un agente conversacional que interactúa por llamada telefónica y WhatsApp.

**Stack clave:** fal.ai (generación), Twilio (telefonía), Whisper (STL), GPT-4o-mini (LLM), FastAPI (orquestación), Redis (cola), Docker (despliegue).

**Sin GPU local.** Todo el contenido pesado se delega a APIs externas.

---

## 2. Arquitectura del Sistema

```
┌────────────────────────────────────────────────────────────────────┐
│                          INTERNET                                   │
└──┬──────────────┬──────────────┬──────────────┬───────────────────┘
   │              │              │              │
   ▼              ▼              ▼              ▼
┌──────┐   ┌──────────┐   ┌─────────┐   ┌──────────┐
│Cliente│   │ Cliente  │   │   Tú    │   │  Admin   │
│WhatsAp│   │ Llamada  │   │ Llamada │   │ Dashboard│
└──┬───┘   └──┬───────┘   └──┬──────┘   └────┬─────┘
   │          │              │                │
   ▼          ▼              ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   CAPA DE ENTRADA (Twilio + Nginx)              │
│  Webhooks WhatsApp  │  Webhooks Voz  │  API REST  │  WebSocket  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ORQUESTADOR (FastAPI)                         │
│                                                               │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Order Manager│  │ Client Manager│  │ Approval Manager    │  │
│  │ - CRUD       │  │ - Fotos      │  │ - Call para aprobar │  │
│  │ - Estados    │  │ - Modelos    │  │ - Timeout / reject  │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         │                 │                      │              │
│         └─────────────────┼──────────────────────┘              │
│                           │                                     │
│         ┌─────────────────▼──────────────────────┐              │
│         │         Task Queue (Redis)              │              │
│         │  order.created → generate.video         │              │
│         │  video.ready → call.for.approval        │              │
│         │  approved → deliver.whatsapp            │              │
│         └─────────────────┬──────────────────────┘              │
└───────────────────────────┼──────────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────────┐
          │                 │                     │
          ▼                 ▼                     ▼
┌─────────────────┐ ┌──────────────┐ ┌────────────────────┐
│   fal.ai        │ │  Twilio      │ │  N8N (opcional)    │
│   Pipeline      │ │  Voice API   │ │  - Facturación     │
│                 │ │              │ │  - CRM             │
│ sync-lipsync/v3 │ │ Llamadas     │ │  - Email marketing │
│ seed-audio-1.0  │ │ WhatsApp     │ │                    │
│ seedance-2.0    │ │ SMS          │ │                    │
└─────────────────┘ └──────────────┘ └────────────────────┘
```

### 2.1 Componentes

| Componente | Tecnología | Puerto | Dependencias |
|---|---|---|---|
| orchestrator | FastAPI + Redis | 8000 | Redis, fal.ai, Twilio |
| fal-wrapper | FastAPI | 8001 | fal.ai SDK |
| redis | Redis 7 | 6379 | — |
| nginx | Nginx | 80/443 | orchestrator |

### 2.2 Diagrama de Estados de una Orden

```
CREATED
   │
   ▼
WAITING_PHOTO ←────────┐
   │                    │
   ▼                    │
PHOTO_RECEIVED          │ (si ya tenía foto)
   │                    │
   ▼                    │
GENERATING_AUDIO        │
   │                    │
   ▼                    │
GENERATING_VIDEO        │
   │                    │
   ▼                    │
AWAITING_APPROVAL ──────┤ (se llama al dueño)
   │                    │
   ├── APPROVED         │
   │   ▼                │
   │   DELIVERING       │
   │   ▼                │
   │   COMPLETED        │
   │                    │
   └── REJECTED         │
       ▼                │
       CANCELLED ───────┘ (se pide nueva foto/guion)
```

---

## 3. Especificación de APIs

### 3.1 API Principal — Orchestrator (`/api/v1`)

#### `POST /api/v1/orders`
Crear una orden nueva.

```json
{
  "client_name": "string (requerido)",
  "client_phone": "string (requerido, formato E.164)",
  "script": "string (requerido, max 500 chars)",
  "style": "enum: 'realistic' | 'professional' | 'friendly' (default: 'realistic')",
  "duration_seconds": "integer (min 15, max 60, default: 30)",
  "source": "enum: 'whatsapp' | 'dashboard' | 'api' (default: 'api')",
  "reference_audio_url": "string? (opcional, para clonar voz)"
}
```

**Response 201:**
```json
{
  "order_id": "ord_a1b2c3d4",
  "status": "created",
  "client_name": "Juan Pérez",
  "estimated_cost_usd": 0.15,
  "created_at": "2026-07-01T12:00:00Z",
  "_links": {
    "self": "/api/v1/orders/ord_a1b2c3d4",
    "status_ws": "wss://sdc.clon/api/v1/ws/ord_a1b2c3d4"
  }
}
```

#### `GET /api/v1/orders/{order_id}`
Estado actual de una orden.

```json
{
  "order_id": "ord_a1b2c3d4",
  "status": "awaiting_approval",
  "client": {
    "name": "Juan Pérez",
    "phone": "+521234567890"
  },
  "video_preview_url": "https://storage.fal.ai/...",
  "audio_preview_url": "https://storage.fal.ai/...",
  "timeline": [
    {"event": "created", "at": "2026-07-01T12:00:00Z"},
    {"event": "photo_received", "at": "2026-07-01T12:01:30Z"},
    {"event": "video_generated", "at": "2026-07-01T12:03:45Z"}
  ],
  "cost_breakdown": {
    "tts": 0.01,
    "video_generation": 0.08,
    "total": 0.09
  }
}
```

#### `POST /api/v1/orders/{order_id}/approve`
Aprobar una orden (vía dashboard o API).

```json
{
  "approved_by": "string (quién aprueba: 'system' | 'owner' | 'client')"
}
```

**Response:**
```json
{
  "status": "delivering"
}
```

#### `POST /api/v1/orders/{order_id}/reject`
Rechazar con opción de motivo.

```json
{
  "reason": "string? (opcional)",
  "retry": "boolean (default: true)"
}
```

#### `POST /api/v1/orders/{order_id}/photo`
Subir foto del cliente (multipart).

```
Content-Type: multipart/form-data
file: (imagen, max 10MB, formatos: jpg, png, webp)
```

#### `POST /api/v1/clients`
Registrar o actualizar cliente.

```json
{
  "phone": "string (E.164, único)",
  "name": "string",
  "email": "string?",
  "photo_url": "string?",
  "voice_reference_url": "string?"
}
```

#### `GET /api/v1/clients/{phone}`
Obtener datos del cliente + historial.

#### `POST /api/v1/call/outbound`
Iniciar llamada saliente (el sistema llama a alguien).

```json
{
  "to": "string (E.164)",
  "purpose": "enum: 'approval' | 'notification' | 'photo_request'",
  "context": {
    "order_id": "string?",
    "client_name": "string?",
    "message": "string?"
  }
}
```

#### `POST /api/v1/call/assistant`
El asistente te llama a ti.

```json
{
  "message": "string (lo que el asistente te dirá al contestar)",
  "priority": "enum: 'low' | 'normal' | 'urgent' (default: 'normal')"
}
```

### 3.2 API Wrapper — fal.ai (`/fal/v1`)

```json
POST /fal/v1/talking-head
{
  "image_url": "string",
  "audio_url": "string",
  "model": "enum: 'sync-lipsync-v3' | 'seedance-2'",
  "webhook_url": "string? (para callback cuando termine)"
}
→ {
  "video_url": "string",
  "cost": 0.08,
  "duration_ms": 4500
}

POST /fal/v1/tts
{
  "text": "string",
  "voice": "enum: 'seed-audio' | 'xai-tts'",
  "reference_audio": "string? (para clonar voz)",
  "language": "enum: 'es' | 'en' (default: 'es')"
}
→ {
  "audio_url": "string",
  "duration_ms": 6000,
  "cost": 0.01
}

POST /fal/v1/train-lora
{
  "images": ["url1", "url2", ...],
  "trigger_word": "string? (default: 'person')",
  "name": "string"
}
→ {
  "lora_id": "lora_abc123",
  "status": "training",
  "estimated_time_seconds": 120
}
```

### 3.3 WebSocket — Tiempo Real

**Endpoint:** `wss://sdc.clon/api/v1/ws`

Eventos que emite el servidor:

```json
{"type": "order.created", "order_id": "ord_..."}
{"type": "order.status", "order_id": "ord_...", "status": "generating_video"}
{"type": "order.ready", "order_id": "ord_...", "preview_url": "https://..."}
{"type": "order.delivered", "order_id": "ord_..."}
{"type": "call.incoming", "from": "+521234567890", "purpose": "photo_request"}
{"type": "error", "order_id": "ord_...", "message": "No se pudo generar video"}
```

Eventos que acepta del cliente:

```json
{"type": "approve", "order_id": "ord_..."}
{"type": "reject", "order_id": "ord_...", "reason": "La voz no suena natural"}
{"type": "call.me", "message": "Llámame urgente"}
```

### 3.4 Webhooks Entrantes (Twilio)

#### WhatsApp Webhook
```
POST /twilio/whatsapp
- Recibe: foto del cliente, mensajes de texto
- Parsea: foto → la guarda y la asocia al cliente
- Responde: confirmación + siguientes pasos
```

#### Voice Webhook (Llamada entrante)
```
POST /twilio/voice
- Recibe: llamada del cliente o del dueño
- Flujo: 
  1. Recibe audio → Whisper STT
  2. Procesa intención con GPT-4o-mini
  3. Responde con Twilio TTS o transfiere
- Cuelga cuando termina
```

#### Voice Status Callback
```
POST /twilio/voice-status
- Recibe: estado de la llamada (completed, busy, no-answer, failed)
- Actualiza: estado de la orden si corresponde
- Reintenta: si fue busy o no-answer, agenda reintento
```

---

## 4. Modelo de Datos

### 4.1 Redis (en memoria con persistencia)

```redis
# Órdenes activas (TTL: 7 días)
order:{id} → hash {
  client_name, client_phone, script, style, duration,
  status, created_at, photo_url, audio_url, video_url,
  fal_audio_cost, fal_video_cost, total_cost
}

# Clientes
client:{phone} → hash {
  name, phone, email, photo_url, voice_ref_url,
  lora_id, total_orders, created_at, last_order_at
}

# Cola de tareas (Redis List / Stream)
queue:orders → list [order_id, order_id, ...]

# Estado de llamadas activas
call:{call_sid} → hash {
  to, purpose, order_id, status, started_at
}

# Sesiones WebSocket
ws:{session_id} → hash {
  user_role, connected_at, last_heartbeat
}

# Contadores (para dashboard)
metrics:videos_today → integer
metrics:videos_this_week → integer
metrics:total_revenue → float
metrics:total_cost → float
metrics:avg_time_to_deliver → float (segundos)
```

### 4.2 Archivos (sistema de archivos + URLs externas)

```
/data/
├── photos/
│   └── {client_phone}/
│       ├── original.jpg        (la foto que mandó)
│       └── processed.png       (recortada/optimizada)
├── audio/
│   └── {order_id}/
│       ├── script.wav          (TTS generado)
│       └── reference.wav       (audio de referencia para clon)
├── videos/
│   └── {order_id}/
│       └── final.mp4           (video entregado)
└── models/
    └── {client_phone}/
        └── lora_info.json      (metadatos del LoRA si se entrena)
```

### 4.3 PostgreSQL (opcional — para persistencia histórica)

Si se decide usar la DB existente en el VPS:

```sql
CREATE TABLE clients (
    phone VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(200),
    photo_url TEXT,
    voice_ref_url TEXT,
    lora_id VARCHAR(50),
    total_orders INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    last_order_at TIMESTAMP
);

CREATE TABLE orders (
    id VARCHAR(20) PRIMARY KEY,
    client_phone VARCHAR(20) REFERENCES clients(phone),
    script TEXT NOT NULL,
    style VARCHAR(20) DEFAULT 'realistic',
    duration_seconds INT DEFAULT 30,
    status VARCHAR(30) NOT NULL DEFAULT 'created',
    photo_url TEXT,
    audio_url TEXT,
    video_url TEXT,
    fal_audio_cost DECIMAL(10,6),
    fal_video_cost DECIMAL(10,6),
    fal_model VARCHAR(50),
    source VARCHAR(20) DEFAULT 'api',
    approved_by VARCHAR(20),
    rejection_reason TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    delivered_at TIMESTAMP,
    delivery_method VARCHAR(20) -- 'whatsapp' | 'email' | 'link'
);

CREATE TABLE order_events (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(20) REFERENCES orders(id),
    event VARCHAR(50) NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE calls (
    sid VARCHAR(50) PRIMARY KEY,
    direction VARCHAR(10) NOT NULL, -- 'inbound' | 'outbound'
    from_number VARCHAR(20),
    to_number VARCHAR(20),
    purpose VARCHAR(30),
    order_id VARCHAR(20) REFERENCES orders(id),
    duration_seconds INT,
    status VARCHAR(20),
    cost DECIMAL(10,6),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_client ON orders(client_phone);
CREATE INDEX idx_orders_created ON orders(created_at DESC);
```

---

## 5. Flujos de Trabajo Detallados

### 5.1 Flujo Completo: Pedido → Entrega

```
CLIENTE                          SISTEMA                          TÚ (DUEÑO)
   │                                │                                │
   │  [Envía foto + texto           │                                │
   │   por WhatsApp]                │                                │
   │ ─────────────────────────────► │                                │
   │                                │  Webhook Twilio WhatsApp       │
   │                                │  POST /twilio/whatsapp         │
   │                                │  │                             │
   │                                │  ▼                             │
   │                                │  Guarda foto en /data/photos/  │
   │                                │  Crea orden (status: created)  │
   │                                │  Responde: "¡Gracias! En        │
   │                                │  unos minutos tendrás tu video"│
   │  ◄──────────────────────────── │                                │
   │                                │                                │
   │                                │  Task Queue: process order     │
   │                                │  │                             │
   │                                │  ▼                             │
   │                                │  1. Generar audio (TTS)       │
   │                                │     POST /fal/v1/tts           │
   │                                │     Con seed-audio-1.0        │
   │                                │     ↓ audio_url               │
   │                                │                                │
   │                                │  2. Generar video (talking    │
   │                                │     head)                     │
   │                                │     POST /fal/v1/talking-head  │
   │                                │     sync-lipsync/v3           │
   │                                │     ↓ video_url               │
   │                                │                                │
   │                                │  3. Marcar estado:            │
   │                                │     awaiting_approval          │
   │                                │                                │
   │                                │  Enciende llamada al dueño    │
   │                                │ ───────────────────────────────►
   │                                │  "Tienes un video de Juan     │
   │                                │   Pérez por aprobar.          │
   │                                │   ¿Lo entrego?"               │
   │                                │                                │
   │                                │  ◄─────────────────────────────│
   │                                │  "Sí, entrégalo"              │
   │                                │                                │
   │                                │  4. Enviar por WhatsApp       │
   │  [Recibe video]                │                                │
   │  ◄──────────────────────────── │                                │
   │                                │                                │
   │                                │  5. Marcar: completed         │
   │                                │  Enviar notificación a ti:    │
   │                                │  "Video entregado con éxito"  │
   │                                │ ───────────────────────────────►
```

### 5.2 Flujo de Llamada del Asistente (te llama a ti)

```
TRIGGER: El sistema completa un video o detecta una anomalía
              │
              ▼
    1. POST /api/v1/call/assistant
       { message: "El video de Juan está listo, ¿lo entrego?" }
              │
              ▼
    2. Twilio crea llamada saliente
       Caller ID: tu número
       Twiml: "<Say>Hola, soy tu asistente de clon digital.
               {mensaje} Di sí para aprobar o no para rechazar.</Say>
               <Gather input='speech' action='/twilio/voice-response'/>"
              │
              ▼
    3. Tú contestas y hablas
       "Sí, entrégalo"
              │
              ▼
    4. Twilio envía grabación a /twilio/voice-response
       Whisper transcribe: "sí entregalo"
       GPT clasifica: intent=approve, confidence=0.97
              │
              ▼
    5. Sistema ejecuta: deliver order
       Envía video por WhatsApp al cliente
       Te envía notificación: "✅ Video entregado"
              │
              ▼
    6. Twilio te dice: "Listo, ya quedó. ¡Que tengas buen día!"
       Cuelga.
```

### 5.3 Flujo de Llamada Entrante (cliente llama)

```
CLIENTE marca al número del sistema
              │
              ▼
    Twilio → POST /twilio/voice
              │
              ▼
    Twiml: "<Say>Hola, soy el asistente de Clon Digital.
            ¿Qué deseas hacer?</Say>
            <Gather input='speech' timeout='5'
                    action='/twilio/voice-intent'/>"
              │
              ▼
    Cliente: "Quiero un video"
              │
              ▼
    Whisper STT → GPT-4o-mini clasifica intención
              │
              ├── "quiero un video" → flujo de nuevo pedido
              │     Pide nombre, guión, pide foto por WhatsApp
              │     → Crea orden, envía link de WhatsApp
              │
              ├── "quiero saber mi pedido" → consulta estado
              │     Busca por teléfono, dice el estado
              │
              ├── "hablar con un humano" → te transfiere la llamada
              │     Twilio: <Dial>{tu número}</Dial>
              │
              └── "gracias" / "adiós" → termina llamada
```

---

## 6. Integraciones Externas

### 6.1 fal.ai
```python
# FAL_KEY en .env
# SDK: pip install fal-client

import fal_client

# Talking head con lip-sync
result = fal_client.subscribe("fal-ai/sync-lipsync/v3/image-to-video", {
    "image_url": "https://...foto.jpg",
    "audio_url": "https://...audio.wav",
    "face_restoration": True,
    "upscale": True,
})
video_url = result["video"]["url"]
cost = 0.08  # por request

# TTS con clon de voz
result = fal_client.subscribe("bytedance/seed-audio-1.0", {
    "prompt": "Hola, este es tu video personalizado...",
    "reference_audio": "https://...voz_referencia.wav",  # opcional
    "target_language": "es",
    "audio_type": "talk",
})
audio_url = result["audio"]["url"]
cost = 0.01  # por request
```

### 6.2 Twilio
```python
# Configuración en .env
TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER
TWILIO_WHATSAPP_NUMBER (formato: whatsapp:+1234567890)

# Llamada saliente (el sistema llama)
call = client.calls.create(
    twiml=f"""<Response>
        <Say voice='Polly.Mia' language='es-ES'>{message}</Say>
        <Gather input='speech' timeout='5'
                action='{base_url}/twilio/voice-response'
                language='es-ES'/>
    </Response>""",
    to=phone,
    from_=TWILIO_PHONE_NUMBER,
    status_callback=f"{base_url}/twilio/voice-status",
    status_callback_event=['completed', 'answered', 'busy', 'no-answer', 'failed'],
)

# WhatsApp saliente
client.messages.create(
    body="¡Aquí está tu video personalizado!",
    media_url=["https://...video.mp4"],
    to=f"whatsapp:{client_phone}",
    from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
)

# Costos aprox: $0.013/min llamada, $0.005/msg WhatsApp
```

### 6.3 Whisper STT (local en el VPS — CPU)
```python
import whisper

model = whisper.load_model("base")  # 1.5GB RAM, corre en CPU
# Alternativa: "tiny" (390MB) para menor latencia

result = model.transcribe("audio.wav", language="es")
text = result["text"].lower().strip()
# → "sí entrégalo"
```

### 6.4 GPT-4o-mini (clasificación de intención)
```python
from openai import OpenAI

client = OpenAI()

def classify_intent(text: str) -> dict:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "system",
            "content": """Clasifica la intención del usuario en una llamada
            sobre un sistema de videos con IA. Responde solo JSON:
            {"intent": "approve|reject|new_order|check_status|speak_human|other",
             "confidence": 0.0-1.0,
             "entities": {"order_id": "...", "reason": "..."}}"""
        }, {
            "role": "user", "content": text
        }],
        temperature=0,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)
```

---

## 7. Despliegue

### 7.1 Estructura de Archivos Final

```
/home/ubuntu/clon-digital/
├── docker-compose.yml
├── Dockerfile.orchestrator
├── Dockerfile.fal-wrapper
├── .env
├── nginx/
│   └── default.conf
├── orchestrator/
│   ├── main.py
│   ├── requirements.txt
│   ├── core/
│   │   ├── __init__.py
│   │   ├── orchestrator.py      # Lógica de orquestación
│   │   ├── models.py            # Pydantic models
│   │   ├── database.py          # Redis + opcional Postgres
│   │   └── config.py            # Settings from .env
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── video_agent.py       # Cliente fal.ai
│   │   ├── voice_agent.py       # TTS + Twilio calls
│   │   ├── messaging_agent.py   # WhatsApp + Email
│   │   └── intent_classifier.py # GPT-4o-mini
│   ├── webhooks/
│   │   ├── __init__.py
│   │   ├── twilio_whatsapp.py   # Webhook WhatsApp entrante
│   │   └── twilio_voice.py      # Webhook voz entrante
│   └── dashboard/
│       ├── __init__.py
│       └── routes.py            # HTML/Streamlit endpoints
├── fal-wrapper/
│   ├── main.py                  # API wrapper de fal.ai
│   ├── requirements.txt
│   └── clients/
│       ├── __init__.py
│       ├── talking_head.py      # sync-lipsync + seedance
│       ├── tts_client.py        # seed-audio + xai-tts
│       └── lora_client.py       # flux-lora training
├── scripts/
│   ├── test_pipeline.sh
│   └── seed_data.py
└── SPEC.md
```

### 7.2 docker-compose.yml (final, sin GPU)

```yaml
version: "3.8"

services:
  orchestrator:
    build:
      context: .
      dockerfile: Dockerfile.orchestrator
    ports:
      - "8000:8000"
    env_file: .env
    volumes:
      - data_photos:/data/photos
      - data_audio:/data/audio
      - data_videos:/data/videos
    depends_on:
      - redis
      - fal-wrapper
    restart: unless-stopped

  fal-wrapper:
    build:
      context: .
      dockerfile: Dockerfile.fal-wrapper
    ports:
      - "8001:8001"
    env_file: .env
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
  data_photos:
  data_audio:
  data_videos:
```

### 7.3 Variables de Entorno (.env)

```bash
# === Sistema ===
ENVIRONMENT=production
LOG_LEVEL=info
SECRET_KEY=...

# === API Keys ===
FAL_KEY=...
OPENAI_API_KEY=...
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_WHATSAPP_NUMBER=+1234567890

# === Tú (dueño) ===
OWNER_PHONE_NUMBER=+1234567890
OWNER_NAME=...

# === FAL.ai config ===
FAL_TALKING_HEAD_MODEL=sync-lipsync/v3/image-to-video
FAL_TTS_MODEL=bytedance/seed-audio-1.0
FAL_LORA_MODEL=fal-ai/flux-lora
FAL_LORA_TRAINER=fal-ai/krea-2-trainer

# === Costos tope ===
MAX_VIDEO_COST_USD=0.50
DAILY_BUDGET_USD=20.00

# === Base URL (para webhooks) ===
BASE_URL=https://sdc.clon

# === Redis ===
REDIS_URL=redis://redis:6379
```

### 7.4 Nginx (proxy reverso)

```nginx
server {
    listen 80;
    server_name sdc.clon;

    location / {
        proxy_pass http://orchestrator:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/v1/ws {
        proxy_pass http://orchestrator:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /fal/ {
        proxy_pass http://fal-wrapper:8001/;
    }

    location /data/ {
        alias /data/;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }
}
```

---

## 8. Monitoreo y Alertas

### 8.1 Métricas a recolectar

```python
# Cada vez que ocurre un evento relevante:

TRACK_SUCCESS = [
    "order_created",        # contador
    "photo_received",       # contador + tiempo desde created
    "audio_generated",      # contador + tiempo + costo
    "video_generated",      # contador + tiempo + costo + modelo usado
    "client_notified",      # contador
    "order_completed",      # contador + tiempo total
    "call_answered",        # contador + duración
    "whatsapp_delivered",   # contador
]

TRACK_FAILURE = [
    "photo_rejected",       # contador + razón (muy grande, formato no soportado, etc.)
    "video_generation_failed",  # contador + error de fal.ai
    "audio_generation_failed",  # contador + error de fal.ai
    "call_failed",          # contador + motivo (busy, no-answer, error)
    "whatsapp_undelivered", # contador
    "approval_timeout",     # contador (no se aprobó en X tiempo)
]
```

### 8.2 Alertas (vía Telegram — ya tienes bot)

```
🚨 [ALERTA] 3 fallos consecutivos en fal.ai
🚨 [ALERTA] Presupuesto diario excedido ($22.50/$20.00)
🚨 [ALERTA] Orden stuck en "generating_video" > 10 minutos
📊 [RESUMEN DIARIO] 15 videos generados, $2.30 costo total, $75 ingresos
```

---

## 9. Plan de Implementación (por módulos)

### Módulo 1 — Fal Wrapper (Día 1-2)
- `fal-wrapper/main.py` — API REST wrapper
- `fal-wrapper/clients/talking_head.py` — sync-lipsync/v3 + seedance-2.0
- `fal-wrapper/clients/tts_client.py` — seed-audio-1.0
- Probar cada endpoint manualmente con curl

### Módulo 2 — Orquestador Core (Día 3-4)
- `orchestrator/core/orchestrator.py` — máquina de estados
- `orchestrator/core/models.py` — Pydantic models
- `orchestrator/core/config.py` — settings
- `orchestrator/agents/video_agent.py` — llama a fal-wrapper

### Módulo 3 — Webhooks Twilio (Día 5-6)
- `orchestrator/webhooks/twilio_whatsapp.py`
- `orchestrator/webhooks/twilio_voice.py`
- `orchestrator/agents/voice_agent.py` — llamadas salientes
- `orchestrator/agents/messaging_agent.py` — WhatsApp
- `orchestrator/agents/intent_classifier.py` — GPT-4o-mini

### Módulo 4 — Dashboard + WS (Día 7)
- WebSocket en tiempo real para el dashboard
- Streaming de eventos de órdenes
- Comandos: approve, reject desde el navegador

### Módulo 5 — Integración con infra existente (Día 8)
- Conectar con n8n (webhooks) para facturación
- Conectar con Jarvis para comandos de voz desde la web
- Usar Redis existente (sdc-redis) o el nuevo

### Módulo 6 — Tests + Despliegue (Día 9-10)
- `scripts/test_pipeline.sh` — prueba end-to-end
- Dockerizar todo
- Desplegar en sdc-prod
- Monitoreo + alertas

---

## Apéndice A: Costos por Video (estimados)

| Componente | Servicio | Costo unitario |
|---|---|---|
| TTS | seed-audio-1.0 (fal.ai) | $0.01 |
| Talking head | sync-lipsync/v3 (fal.ai) | $0.08 |
| STT | Whisper local (CPU) | $0.00 |
| LLM clasificación | GPT-4o-mini | $0.0005 |
| Llamada (30s) | Twilio | $0.0065 |
| WhatsApp (video) | Twilio | $0.005 |
| Almacenamiento | S3/Backblaze (~50MB/video) | $0.000001 |
| **Total por video** | | **~$0.10** |

Precio al cliente sugerido: **$5-15 USD por video** → margen 98-99%.

## Apéndice B: Limitaciones Conocidas

1. **Calidad de sync-lipsync/v3**: Funciona mejor con fotos frontales iluminadas. Perfiles y fotos con obstrucciones pueden dar peor resultado.
2. **Clon de voz con seed-audio**: Requiere 3-10 segundos de audio limpio (sin ruido de fondo). Una llamada telefónica no es ideal para capturar el reference audio.
3. **Latencia**: sync-lipsync tarda 30-60 segundos en generar. No es tiempo real.
4. **Consistencia facial**: Sin LoRA, la cara puede variar ligeramente entre frames. Para uso profesional, entrenar LoRA con krea-2-trainer (5-10 fotos, ~$1, 2 min de entrenamiento).
5. **Dependencia externa**: Si fal.ai cae, el sistema no puede generar contenido. Tener seedance-2.0 como fallback.
