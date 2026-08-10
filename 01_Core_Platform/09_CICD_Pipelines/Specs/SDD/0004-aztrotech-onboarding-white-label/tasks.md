# Tasks 0004: Aztrotech Onboarding Inteligente + White-Label

## Fase 1: Core Onboarding Aztrotech (P0)

### T1.1 — Tests TDD: routing, lead capture, scheduling, notification
**Archivo**: `tests/integration/test_aztrotech_onboard.py`
**Criterios**:
- `test_routing_aztrotech`: bot_name "Aztro_tech_bot" → tenant "aztrotech", agent "cesar"
- `test_lead_capture_schema`: LLM devuelve JSON con campos obligatorios (nombre, empresa, servicio, fecha, hora)
- `test_scheduling_conflict`: dos leads misma fecha/hora → rechaza segundo
- `test_notification_cesar`: formato correcto, ambos canales (Telegram + WhatsApp)
- `test_okf_pricing_exacto`: respuesta precio usa SOLO valores de aztrotech.pricing.json
- `test_escalation_dificil`: intención "tecnico/dificil" → notifica César + "te paso con él"

### T1.2 — onboarding_engine.py (Motor Determinista)
**Archivo**: `01_Core_Platform/03_Agentic_Infrastructure/onboarding_engine.py`
**Responsabilidades**:
- `capture_lead(tenant, chat_id, fields_dict)` → valida campos, persiste SQLite, retorna lead_id
- `schedule_cita(lead_id, fecha, hora)` → valida disponibilidad (SQLite), zona horaria America/Hermosillo, confirma
- `notify_cesar(lead_id)` → formatea template, envía Telegram + WhatsApp (wacli), log
- `get_lead(lead_id)` / `update_lead(lead_id, fields)` → CRUD simple
- `check_availability(fecha, hora)` → determinista, sin LLM
**Regla**: Cero LLM. Todo determinista. LLM solo en lead_classifier.

### T1.3 — lead_classifier.py (LLM + Schema JSON)
**Archivo**: `01_Core_Platform/03_Agentic_Infrastructure/lead_classifier.py`
**Entrada**: `(tenant, mensaje_texto, contexto_previo_opcional)`
**Salida**: JSON estricto:
```json
{
  "intencion": "nuevo_lead|agendar_cita|precio|info_general|tecnico_dificil|escalar_cesar",
  "campos": {"nombre": "", "empresa": "", "servicio": "", "fecha": "", "hora": ""},
  "confianza": 0.0-1.0,
  "respuesta_sugerida": "texto para el lead (si aplica)",
  "accion_requerida": "capture|schedule|notify|escalar|responder"
}
```
**Implementación**: `sdc_sdk.call_llm()` con `response_format: json_schema` + schema Pydantic. Modelo: deepseek-v4-flash-0731. Temperature 0.1.

### T1.4 — voice_pipeline.py (Wrapper Unificado)
**Archivo**: `01_Core_Platform/03_Agentic_Infrastructure/voice_pipeline.py`
**Funciones**:
- `stt_audio(audio_path) -> str`: faster-whisper small int8, CPU, español
- `tts_text(text, voice) -> ogg_path`: edge-tts + ffmpeg imageio (reusa voice_reply.py)
- `send_voice(bot, chat_id, text, voice)`: TTS + sendTelegramVoice (reusa voice_reply.py)
- `process_voice_message(bot, chat_id, audio_path) -> str`: STT → lead_classifier → onboarding_engine → TTS response → send
**Regla**: Determinista salvo STT (modelo). LLM solo en lead_classifier.

### T1.5 — Extender multi_tenant_webhook.py
**Archivo**: `02_Client_Projects/Aztrotech/03_Media_Assets/webhooks/multi_tenant_webhook.py`
**Cambios**:
- `do_POST`: detectar `media_path` (voice) → `voice_pipeline.stt_audio` → texto → `route_message`
- Nuevo endpoint `/webhook/voice` para widget web (recibe audio blob)
- Respuesta: `{status, tenant, agent, lead_id, response_text, response_voice_path}`

### T1.6 — Extender tenant_router.py
**Archivo**: `02_Client_Projects/Aztrotech/03_Media_Assets/tenant_router.py`
**Nueva función**:
```python
def route_message(bot_name: str, user_id: str, message: str, media_path: str = None) -> dict:
    """Rutea mensaje completo: STT si hay media → classifier → engine → response"""
    # 1. get_tenant_for_bot(bot_name)
    # 2. si media_path: texto = stt_audio(media_path)
    # 3. classification = lead_classifier.classify(tenant, texto)
    # 4. Ejecutar acción según classification.accion_requerida
    # 5. Generar respuesta (texto + opcional voz)
    # 6. Return dict con todo lo necesario para webhook response
```

### T1.7 — SQLite Leads Schema
**Archivo**: `01_Core_Platform/03_Agentic_Infrastructure/Databases/Aztrotech_Citas/leads.db`
**Tabla**:
```sql
CREATE TABLE leads (
    id TEXT PRIMARY KEY,
    tenant TEXT NOT NULL,
    chat_id TEXT NOT NULL,
    nombre TEXT,
    empresa TEXT,
    servicio TEXT,
    fecha TEXT,      -- ISO UTC
    hora TEXT,       -- HH:MM
    estado TEXT DEFAULT 'nuevo',  -- nuevo, calificado, cita_agendada, escalado, cerrado
    canal TEXT,      -- telegram, whatsapp, web
    creado_en TEXT DEFAULT (datetime('now')),
    actualizado_en TEXT DEFAULT (datetime('now')),
    notas TEXT
);
CREATE INDEX idx_leads_tenant_fecha ON leads(tenant, fecha);
```

### T1.8 — Entry Point: run_onboarding.py
**Archivo**: `01_Core_Platform/03_Agentic_Infrastructure/run_onboarding.py`
- Inicia webhook server (puerto 5289)
- Scheduler recordatorios (cron diario 9am: leads sin respuesta 24h → re-engage)
- Health check `/health`
- Logging estructurado

---

## Fase 2: White-Label Provisioning (P1)

### T2.1 — provision_tenant.py
**Archivo**: `01_Core_Platform/Infrastructure/sonora-digital-corp/scripts/provision_tenant.py`
**CLI**:
```bash
python3 provision_tenant.py \
  --tenant miempresa \
  --bot @miempresa_bot \
  --owner "Juan Pérez" \
  --cliente "MiEmpresa SA" \
  --voz es-MX-JorgeNeural \
  --canales telegram,whatsapp,web \
  --okf-concepts miempresa.pricing,miempresa.faq
```
**Acciones**:
1. `tenant_router.register_new_tenant(...)` → registry
2. Crear `tenants/miempresa/` con: `config.yaml`, `policies.yaml`, `server.py`, `web/index.html`
3. Generar `OKF` concepts placeholder si no existen
4. Output: "Tenant miempresa listo. Bot: @miempresa_bot. Landing: tenants/miempresa/web/"

### T2.2 — Landing Page Plantilla (index.html)
**Archivo**: `01_Core_Platform/Infrastructure/sonora-digital-corp/tenants/{tenant}/web/index.html`
**Características**:
- Three.js background (reusa Mysticgrimoire)
- Branding configurable: colores, logo, nombre empresa
- Botón WhatsApp (wa.me link con ref tenant)
- Widget voz (MediaRecorder → POST /webhook/voice)
- Chat embebido opcional (iframe al bot)
- Responsive, PWA-ready

### T2.3 — config.yaml Plantilla
**Archivo**: `01_Core_Platform/Infrastructure/sonora-digital-corp/tenants/{tenant}/config.yaml`
Basado en Aztrotech config.yaml, parametrizado: tenant_id, display_name, owner, voice, model, rate_limits.

### T2.4 — policies.yaml Plantilla
**Archivo**: `01_Core_Platform/Infrastructure/sonora-digital-corp/tenants/{tenant}/policies.yaml`
Basado en Aztrotech policies.yaml, parametrizado: allowed_domains, rate_limits por paquete.

### T2.5 — Test Provision
**Archivo**: `tests/integration/test_provision_tenant.py`
- Provision tenant "testcorp"
- Verificar: registry tiene entry, directorio creado, config.yaml válido, index.html sirve, webhook rutea a testcorp

---

## Fase 3: Multi-Canal + Voz Completa (P1)

### T3.1 — Validar whisper_stt.py
**Archivo**: `01_Core_Platform/04_Automations_and_Workflows/02_Voice_Agents/whisper_stt.py`
- faster-whisper small int8, CPU, español
- Benchmark: < 2s para audio 10s

### T3.2 — Handler Voice Telegram
**Archivo**: `01_Core_Platform/04_Automations_and_Workflows/01_Telegram_Bots/webhook_voice.py`
- Recibe `voice` update → descarga → STT → route_message

### T3.3 — Widget Voz Web
**Archivo**: `01_Core_Platform/Infrastructure/sonora-digital-corp/tenants/{tenant}/web/voice_widget.js`
- MediaRecorder → blob → POST /webhook/voice con tenant header
- UI: botón micrófono, visualizador, estado

### T3.4 — WhatsApp Business API (cuando esté)
- wacli bridge → webhook mismo formato

---

## Fase 4: Dashboard César (P2)

### T4.1 — cesar_dashboard.py
**Archivo**: `01_Core_Platform/10_Client_Interfaces/Telegram_Handlers/cesar_dashboard.py`
- Comando `/leads` → lista leads día (estado, nombre, empresa, hora)
- Comando `/lead <id>` → detalle + botones inline: "Llamar ahora", "Reagendar", "Cerrar"
- Callback handlers → actualiza SQLite + notifica lead