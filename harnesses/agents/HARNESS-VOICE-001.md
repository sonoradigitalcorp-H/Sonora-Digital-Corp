# Agent Harness — Voice Agent (Mystic)

**Inherits**: OMEGA PROMPT v10.0 + SOUL.md
**Template**: AGENT-HARNESS-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: HARNESS-VOI-001
**Status**: Live

---

## 1. Mission

Asistente telefónico IA 24/7 que recibe llamadas de voz, entiende intención, responde con voz natural y soundscapes, y redirige a calendario, pricing o agente humano — sin intervención humana.

## 2. Functional Requirements

```
FR-VOICE-01: WebSocket bidireccional debe aceptar audio PCM16 a 16kHz y texto
FR-VOICE-02: VAD debe detectar silencio >800ms como fin de utterance
FR-VOICE-03: Whisper STT debe transcribir español mexicano con <3s de latencia
FR-VOICE-04: Intent Router debe clasificar en <500ms con regex + LLM fallback
FR-VOICE-05: LLM (DeepSeek V4 Flash via MCP) debe generar respuesta contextual
FR-VOICE-06: TTS (Edge TTS) debe sintetizar voz femenina mexicana en <2s
FR-VOICE-07: Soundscapes deben reproducirse en loop de fondo sin interrumpir voz
FR-VOICE-08: Sesiones deben persistir en Engram con importancia ≥2
FR-VOICE-09: Debe soportar cambio de tono (warm/energetic/calm/professional) en vivo
FR-VOICE-10: Debe emitir eventos de sesión a events.jsonl
```

## 3. Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    VOICE AGENT — MYSTIC                          │
│                                                                  │
│  Frontend (HTML/JS)                                              │
│  ┌──────────────────────────┐                                    │
│  │  WebSocket (PCM16/JSON)  │◄──────────────────┐               │
│  └──────────┬───────────────┘                    │               │
│             │ audio/text                         │               │
│             ▼                                    │               │
│  ┌──────────────────┐    ┌──────────────────┐    │               │
│  │  VAD Detection   │───►│  Whisper STT     │    │               │
│  │  (silence 800ms) │    │  (es-MX, 16kHz)  │    │               │
│  └──────────────────┘    └────────┬─────────┘    │               │
│                                  │ text          │               │
│                                  ▼               │               │
│  ┌──────────────────────────────────────────┐    │               │
│  │         Intent Router                     │    │               │
│  │  ┌──────────┐  ┌──────────┐  ┌────────┐ │    │               │
│  │  │ Regex    │  │ LLM      │  │ Fallback│ │    │               │
│  │  │ (500ms)  │─►│ (3s)     │─►│ (chat)  │ │    │               │
│  │  └──────────┘  └──────────┘  └────────┘ │    │               │
│  └───────────────────┬──────────────────────┘    │               │
│                      │ intent                    │               │
│                      ▼                           │               │
│  ┌──────────────────────────────────────────┐    │               │
│  │         Response Engine                   │    │               │
│  │  ┌──────────┐  ┌──────────────────────┐  │    │               │
│  │  │ Template │  │  LLM (MCP Gateway)   │  │    │               │
│  │  │ (instant)│  │  deepseek-v4-flash   │  │    │               │
│  │  └──────────┘  └──────────┬───────────┘  │    │               │
│  └───────────────────────────┼──────────────┘    │               │
│                              │ response          │               │
│                              ▼                   │               │
│  ┌──────────────────────────────────────────┐    │               │
│  │         Audio Pipeline                    │    │               │
│  │  ┌──────────┐  ┌──────────┐  ┌────────┐ │    │               │
│  │  │ Edge TTS │─►│ Audio    │─►│ Mix    │ │    │               │
│  │  │ (es-MX)  │  │ Mixer    │  │ PCM16  │ │    │               │
│  │  └──────────┘  └──────────┘  └────────┘ │    │               │
│  └───────────────────┬──────────────────────┘    │               │
│                      │ audio + events            │               │
│                      ▼                           │               │
│  ┌──────────────────────────────────────────┐    │               │
│  │         MCP Gateway (127.0.0.1:18989)    │    │               │
│  │  ┌──────────┐  ┌──────────┐  ┌────────┐ │    │               │
│  │  │ Engram   │  │ Neo4j    │  │ Qdrant  │ │    │               │
│  │  │ (memory) │  │ (graph)  │  │ (RAG)   │ │    │               │
│  │  └──────────┘  └──────────┘  └────────┘ │    │               │
│  └──────────────────────────────────────────┘    │               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 4. Capabilities

```
Capabilities:
- Voice Interaction: Receive, transcribe, and respond to voice calls 24/7
  Events: voice_session_started, voice_input_received, voice_response_sent
- Intent Classification: Classify user intent via regex + LLM fallback
  Events: intent_classified, intent_routed
- Appointment Booking: Route calls to calendario for scheduling
  Events: booking_requested, booking_redirected
- Product Inquiry: Answer pricing, services, and product questions
  Events: pricing_requested, services_requested
- Redirect to Human: Route to WhatsApp or contact form when needed
  Events: human_transfer_requested
- Session Memory: Store voice sessions in Engram for continuity
  Events: session_memory_saved
```

## 5. Skills

```
Skills:
- voice-interaction: Full voice pipeline (STT → Intent → LLM → TTS → Soundscape)
  Source: apps/voice-realtime/server.py
- intent-routing: Classify and route voice intents
  Source: apps/voice-realtime/intent_router.py
- voice-templates: Dynamic response templates with variation
  Source: apps/voice-realtime/voice_templates.py
- mcp-client: Unified MCP gateway client
  Source: apps/voice-realtime/mcp_client.py
- soundscapes: Ambient audio generation
  Source: apps/voice-realtime/pipeline/audio_mixer.py
```

## 6. Policies

```
Policies:
- Every voice session MUST be stored in Engram with importance ≥2
- Audio data MUST NOT be persisted after session ends (privacy)
- VAD timeout set to 800ms silence for utterance detection
- LLM fallback uses MCP Gateway first, then direct OpenRouter
- Soundscapes default by time of day (nature/energético/cálido/minimal)
- No PII may be logged in plain text; session IDs are pseudonymous
- Rate limit: max 60 sessions/minute per IP
- Tone can be changed mid-session via WebSocket message
```

## 7. Memory Scope

```
Memory Scope:
  Read: Layer 1 (Working), Layer 2 (Task), Layer 4 (Customer)
  Write: Layer 1 (Working), Layer 2 (Task), Layer 6 (Historical)
```

## 8. Approval Requirements

```
Approval Requirements:
- voice response: none (automatic)
- human transfer: none (automatic redirect)
- session memory delete: none
- product recommendation: none
- pricing quotation: none
- tone override by user: none
- booking confirmed: notify
```

## 9. Failure Modes

```
Failure Modes:
- MCP Gateway down: brain_context and LLM unavailable (fallback to templates + direct OpenRouter)
- TTS engine fail: Edge TTS rate-limited or down (fallback to text-only response)
- Whisper STT fail: transcription returns empty or errors (request repetition)
- WebSocket disconnect: client drops before response (log, close session)
- VAD false positive: silence detected mid-speech (ignore if <640 bytes)
- LLM timeout: >10s without response (fallback to template)
```

## 10. Recovery Procedures

```
Recovery Procedures:
- MCP Gateway down: cache last brain context, use direct OpenRouter call, retry every 30s
- TTS engine fail: send text-only response with status "text_mode", retry TTS next interaction
- Whisper STT fail: send error template asking for repetition, re-init VAD
- WebSocket disconnect: save partial session to Engram, clean up soundscape task
- VAD false positive: set minimum audio threshold (640 bytes = 40ms)
- LLM timeout: use template response, flag degraded state
```

## 11. Metrics

```
Metrics:
- session_duration: Given session start When session end Then seconds
  Target: < 10min average
- intent_accuracy: Given user utterance When classified Then correct match rate
  Target: > 90%
- response_latency: Given audio input When response sent Then ms total
  Target: < 5s p95
- tts_latency: Given text When audio ready Then ms
  Target: < 2s p95
- stt_accuracy: Given audio When transcribed Then WER
  Target: < 10% WER
- session_completion: Given session started When resolved Then rate
  Target: > 85%
```

## 12. Tests

```gherkin
Feature: Voice Agent
  Scenario: User calls and asks for pricing
    Given a WebSocket connection is established
    When user sends audio or text "¿cuánto cuestan sus servicios?"
    Then intent is classified as "go_pricing"
    And response template for pricing is selected
    And TTS audio is returned within 5s
    And session is saved to Engram

  Scenario: User wants to book appointment
    Given a WebSocket connection is established
    When user says "quiero agendar una cita"
    Then intent is classified as "book_appointment"
    And redirect URL to calendario is sent
    And booking_requested event fires

  Scenario: User speaks but audio is too short
    Given a WebSocket connection is established
    When user sends <640 bytes of audio
    Then audio buffer is ignored
    And VAD continues listening

  Scenario: LLM fallback on template miss
    Given a WebSocket connection is established
    When user asks a question with no matching template
    Then Intent Router falls back to "talk" type
    And LLM generates a response via MCP Gateway
    And TTS synthesizes the response

  Scenario: Change soundscape mid-session
    Given an active voice session
    When user sends {"type": "change_soundscape", "soundscape": "nature"}
    Then soundscape changes to "nature"
    And new soundscape audio starts looping
```

## 13. API Endpoints

```
WebSocket:
  ws://<host>:8900/v1/chat     — Full voice session (audio + text)
  ws://<host>:8900/v1/chat/text — Text-only session (no audio)

REST:
  GET  /api/health             — Health check (status, active_sessions, soundscape)
  GET  /api/soundscapes        — List available soundscapes
  GET  /                       — Frontend HTML (mystic_voice.html)
  GET  /chat                   — Frontend HTML (alias)

WebSocket Message Types:
  → input_text                    — User sends text
  → input_audio_buffer.append     — User sends audio chunk (base64 PCM16)
  → input_audio_buffer.commit     — User signals end of utterance
  → change_soundscape             — Change background audio
  → change_tone                   — Change voice tone
  ← session.created               — Session initialized
  ← status                        — Status update (listening, understanding, etc.)
  ← response.audio.delta          — TTS audio chunk (base64)
  ← soundscape.delta              — Background audio chunk (base64)
  ← response.output_text.delta    — Text response
  ← redirect                      — URL redirect command
  ← response.done                 — Response complete
```

## 14. Configuration

```yaml
# config/voice-agent.yaml
voice_agent:
  port: 8900
  host: "127.0.0.1"
  sample_rate: 24000
  input_sample_rate: 16000
  mcp_gateway: "http://127.0.0.1:18989"
  tts:
    provider: "edge"
    voice: "es-MX-DaliaNeural"
    fallback_provider: "gcloud"
    fallback_voice: "es-MX-Wavenet-A"
  intent_router:
    use_llm_fallback: true
    confidence_threshold: 0.5
  vad:
    silence_timeout_ms: 800
    min_audio_bytes: 640
  soundscapes:
    default: "minimal"
    schedule:
      - hour: [6, 12]
        soundscape: "nature"
      - hour: [12, 18]
        soundscape: "energetico"
      - hour: [18, 22]
        soundscape: "calido"
      - hour: [22, 6]
        soundscape: "minimal"
  session:
    timeout_seconds: 300
    max_history: 10
  tone:
    default: "warm"
    allowed: ["warm", "energetic", "calm", "professional"]
```

## 15. Database Schema

```
Engram (SQLite + FTS5):
─────────────────────────────────────────────────
Key: voice_session:{session_id}:{timestamp}
Value: JSON { user_text, response, intent, destination, tone }
Layer: 2 (task)
Importance: 2 (high)
Tags: "voice,{intent_id}"

In-Memory Sessions (SESSIONS dict):
─────────────────────────────────────────────────
session_id: str (uuid4, 8 chars)
  ├── created_at: float (timestamp)
  ├── interaction_count: int
  ├── tone: str (warm|energetic|calm|professional)
  ├── history: list[dict] (max 10 messages)
  └── session_id: str
```

## 16. Reseller / White-Label Setup

```yaml
reseller:
  enabled: true
  markup: 30-50% over base price
  branding:
    agent_name: "Mystic"          # Configurable per tenant
    voice_id: "es-MX-DaliaNeural" # Configurable per reseller
    welcome_message: null          # Custom greeting per tenant
    soundscape_default: "minimal"
  tenant_config:
    - tenant_id: "{reseller_slug}"
      tone: "warm"
      products: []                  # Custom product catalog
      redirect_rules:
        booking: "{reseller_booking_url}"
        contact: "{reseller_whatsapp}"
  features:
    white_label_domain: true        # Agent runs on reseller's subdomain
    custom_templates: true          # Reseller can override voice templates
    custom_soundscapes: true        # Reseller can upload custom soundscapes
    analytics_dashboard: true       # Per-tenant usage metrics
  setup_steps:
    1. Create tenant entry in config/tenants.json
    2. Configure voice_id and agent_name per tenant
    3. Set redirect URLs for booking, pricing, contact
    4. Configure products catalog (or use default)
    5. Deploy with VOICE_PORT and MCP_GATEWAY_URL env vars
    6. Test with voice call simulation
```

## 17. Pricing

```
Base License:   $149/license/month
Includes:       Up to 500 sessions/month, 5 soundscapes, all tones
Overages:       $0.05/session after 500

Reseller Tiers:
  Starter:      $149/mo — up to 1,000 sessions, 1 tenant
  Professional: $499/mo — up to 5,000 sessions, 5 tenants
  Enterprise:   $1,499/mo — unlimited sessions, unlimited tenants, white-label

Add-ons:
  Custom Voice:     $99 one-time (train custom TTS voice)
  Custom Soundscape:$199 one-time (produce custom ambient audio)
  SMS Fallback:     $49/mo (text response when TTS unavailable)
```

## 18. Setup Steps

```bash
# 1. Clone and install dependencies
cd ~/sdc
pip install -r apps/voice-realtime/requirements.txt

# 2. Set environment
export VOICE_PORT=8900
export MCP_GATEWAY_URL=http://127.0.0.1:18989
export OPENROUTER_API_KEY=sk-or-...  # fallback LLM

# 3. Start the voice server
python apps/voice-realtime/server.py

# 4. Verify health
curl http://127.0.0.1:8900/api/health

# 5. Open frontend
# Navigate to http://127.0.0.1:8900 in a browser

# Docker deployment
docker compose -f infra/docker-compose.yml up -d sdc-jarvis-webui
# Voice runs inside the webui container on port 8900
```

## 19. Testing Instructions

```bash
# Unit tests
pytest apps/voice-realtime/tests/ -v

# Test Intent Router
python -c "
from apps.voice_realtime.intent_router import IntentRouter
router = IntentRouter()
result = router.route('quiero agendar una cita')
print(f'Intent: {result.payload[\"intent_id\"]} → {result.destination}')
assert result.payload['intent_id'] == 'book_appointment'
"

# Test voice template engine
python -c "
from apps.voice_realtime.voice_templates import VoiceTemplateEngine
tpl = VoiceTemplateEngine()
resp = tpl.get_response('go_pricing', {'min_price': '199'})
print(f'Template: {resp}')
assert '{min_price}' not in resp  # variable replaced
"

# Test WebSocket connection (text only)
python -c "
import asyncio, websockets, json
async def test():
    async with websockets.connect('ws://127.0.0.1:8900/v1/chat') as ws:
        init = await ws.recv()
        print(f'Session: {json.loads(init)[\"session\"][\"id\"]}')
        await ws.send(json.dumps({'type': 'input_text', 'text': 'Hola'}))
        resp = await ws.recv()
        print(f'Response received')
asyncio.run(test())
"

# Integration test: full audio pipeline
pytest tests/integration/test_voice_pipeline.py -v

# Load test: 50 concurrent sessions
python scripts/load-test-voice.py --concurrent 50 --duration 60
```

## 20. Observability

```
Observability:
- Health endpoint: GET /api/health
- Active sessions: GET /api/health → active_sessions field
- Events: state/events/events.jsonl
- Logs: standard output (structured JSON via uvicorn)
- Metrics: session_duration, intent_accuracy, response_latency, tts_latency
- Log level: INFO (set via VOICE_LOG_LEVEL env var)
- Tracing: LangFuse (when available) via MCP Gateway
```

## 21. Dependencies

```
Dependencies:
- MCP Gateway: service (port 18989, for brain context, LLM, Engram)
- Edge TTS: Python lib (Microsoft Edge TTS API)
- Whisper: Python lib (local STT)
- FastAPI + Uvicorn: HTTP/WebSocket server
- httpx: async HTTP client for MCP and OpenRouter
- numpy: audio processing
- Engram MCP: memory persistence
- Neo4j MCP: knowledge graph (optional)
- Qdrant MCP: vector search (optional)
```

## Validation Checklist

- [x] Mission is one sentence, measurable
- [x] All FRs are numbered and testable
- [x] Architecture diagram describes data flow
- [x] All capabilities map to events
- [x] DB schema defined
- [x] API endpoints fully documented
- [x] All failure modes have recovery procedures
- [x] Reseller/white-label configuration documented
- [x] Pricing defined with tiers
- [x] Setup steps are executable
- [x] Tests cover happy path, edge cases, and failure modes
- [x] Observability endpoints defined
