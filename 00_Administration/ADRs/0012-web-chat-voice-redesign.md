# ADR 0012: Rediseño Web Chat + Voz Pro Max (SDD-0012)

**Fecha**: 2026-08-22/23  
**Estado**: IMPLEMENTADO Y DESPLEGADO  
**Autor**: MYSTIC / SDC

## Contexto

El chat web existente (`index.html`, `chat.html`, `hermosillo.html`) usaba:
- Web Speech API (Chrome-only, sin control de voz servidor)
- Orbe Three.js básico sin reactividad audio
- Sin catálogo de asistentes, sin agenda visible
- TTS via browser `speechSynthesis` (limitado, sin stop)
- Copy con signos de exclamación y menciones técnicas ("IA", "bot", "modelo")

**Objetivo**: Rediseño completo hacia UI Pro Max (Netflix/Spotify UX):
- Three.js orbe 3D reactivo al audio (GPU particles + shader fresnel)
- Glassmorphism system (backdrop-filter blur 24px)
- Catálogo 8 nichos con ahorros $/mes + demo en chat
- Agenda visible con 10 días hábiles + 8 slots → POST `/api/v1/citas` → TTS + wacli WhatsApp
- Mic push-to-talk (MediaRecorder) → STT servidor → chat → TTS servidor → audio + orb pulse
- Comando silencio ("calla/silencio/basta")
- CERO dashboard, CERO exclamaciones, CERO tecnicismos
- Todo cómputo pesado en VPS OVH

## Decisiones Clave

### 1. Stack de Voz 100% Servidor (VPS OVH)
| Componente | Tech | Ubicación | Justificación |
|------------|------|-----------|---------------|
| STT | faster-whisper small int8 | :5292 | CPU-only, ~2.6s/4s audio, 0 tokens, privado |
| TTS | edge-tts (Dalia/Jorge) | :5293 | Rápido (~1s), streaming MP3, 0 tokens |
| LLM | nemotron-3-ultra-free (primary) | OpenRouter | Eval 83% vs deepseek 50%, gratis, rápido |

**Regla de oro**: Cero modelos pesados en laptop (3.3GB RAM). Todo en VPS OVH 11GB RAM.

### 2. Nemotron-free como Primary (Decision Data-Driven)
**Eval resultado** (6 casos × 2 modelos, juez nemotron-free):
- nemotron: **83% pass** (5/6) — rápido 2-8s, copy de venta superior
- deepseek-0731: **50% pass** (3/6) — lento 20-40s, frecuente timeout→content vacío

**Acción**: Invertir `MODEL_CHAIN` en `vps_ai_server.py`:
```python
MODEL_CHAIN = [
    "nvidia/nemotron-3-ultra-550b-a55b:free",  # primary
    "deepseek/deepseek-v4-flash-0731",          # fallback
]
```

### 3. Recorte de Respuesta para Voz (Hard Constraint)
nemotron tiende a respuestas largas (>500 chars) → malas para TTS.
**Implementación**: `clean_reply()` corta a ~320 chars en frase completa + `max_tokens: 220`.

### 4. SOUL Server-Side (Determinista)
System prompts inyectados en servidor por `person` (sdc/nathaly):
- Reglas duras: 0 exclamaciones, 0 tecnicismos, beneficios-first
- Objeciones manejadas (caro→más barato que recepcionista; miedo tech→no tocas nada; etc.)
- **SIEMPRE cierra con 2 horarios concretos** (martes 10 / jueves 4)
- **NUNCA repite escenario** de respuesta anterior

### 5. UI Single-File SPA (`chat_pro_max/index.html`)
- Three.js orbe CPU-displaced (2562 verts, 60fps) + 520 partículas GPU
- Glassmorphism CSS variables per persona
- Catálogo 8 nichos (rail Netflix) con ahorros explícitos
- Agenda modal → POST `/api/v1/citas` → TTS + wacli
- Comando silencio regex `SILENCE_RE`
- Fix mic: umbral 300B, error handling, sin `alert()`

### 6. wacli Binary (Go) — No NPM
`wacli 0.12.0` es binario Go propietario. VPS reprovisionado perdió el binario; copiado de laptop → `/home/mystic/.local/bin/wacli` (AUTHENTICATED=true, JID 5216623538272). `npm i wacli` **NO existe**.

---

## Alternativas Consideradas y Rechazadas

| Alternativa | Por qué NO |
|-------------|------------|
| Web Speech API (browser STT/TTS) | Chrome-only, sin control servidor, sin stop confiable |
| Kokoro ONNX local en VPS | No instalado aún; edge-tts funciona y es 0 tokens |
| deepseek-0731 primary | Eval probó: 50% pass, timeouts frecuentes, vacío content |
| React/Vue SPA build | Overhead innecesario; single-file HTML deployable directo a nginx |
| Dashboard admin | Usuario pidió CERO dashboard — solo valor visible |

---

## Consecuencias

### Positivas
- ✅ Latencia chat: **~2.9s** (vs 20-40s deepseek)
- ✅ Copy venta: 83% eval pass, beneficios concretos, 0 exclamaciones
- ✅ Voz E2E: mic→STT→chat→TTS→orb pulse + WhatsApp audio confirmación
- ✅ Costo: nemotron-free = $0; edge-tts = $0; whisper CPU = $0
- ✅ Tests: 22/22 PASS (soul cleaning, UI, catálogo, agenda, silencio, endpoints)

### Negativas / Riesgos
- ⚠️ nemotron a veces responde largo → mitigado con corte 320 chars
- ⚠️ wacli binary management manual (no package manager)
- ⚠️ Nemotron free tier podría cambiar límites futuros
- ⚠️ FAL_KEY vencida (imágenes catálogo pendientes)

---

## Métricas de Éxito (Definition of Done)

| Métrica | Target | Actual |
|---------|--------|--------|
| Latencia chat (p95) | <3s | 2.9s |
| Eval nemotron pass rate | >80% | 83% |
| 0 exclamaciones en respuestas | 0 | 0 (test automatizado) |
| Copy sin tecnicismos | 100% | 100% |
| Cita E2E guardada + WhatsApp audio | ✅ | ✅ (Cliente E2E 24/08 11:00) |
| Tests PASS | 100% | 22/22 |

---

## Archivos Clave Creados/Modificados

```
01_Core_Platform/04_Automations_and_Workflows/vps_ai_server.py      # REWRITE v2
01_Core_Platform/03_Agentic_Infrastructure/voice/stt_server.py      # NEW
01_Core_Platform/03_Agentic_Infrastructure/voice/tts_server.py      # NEW
02_Client_Projects/Sonora_Digital_Corp/04_Deployment/chat_pro_max/index.html  # NEW (UI Pro Max)
01_Core_Platform/01_Architecture/SOUL.md                            # UPDATED (versión voz)
01_Core_Platform/09_CICD_Pipelines/Specs/SDD/0012-web-chat-voice-redesign.md  # NEW (spec)
prompt_registry/eval_prompts.yaml + run_eval.py                     # NEW (eval)
03_Sandbox_and_RnD/tests/integration/test_sdd0012_web_chat.py       # NEW (22 tests)
BLUEPRINT.md                                                        # NEW (este blueprint)
```

---

## Referencias
- SPEC: `01_Core_Platform/09_CICD_Pipelines/Specs/SDD/0012-web-chat-voice-redesign.md`
- EVAL: `prompt_registry/eval_prompts.yaml` + `run_eval.py`
- SOUL: `01_Core_Platform/01_Architecture/SOUL.md`
- BLUEPRINT: `BLUEPRINT.md`
- ESTADO: `ESTADO.md` (sección SDD-0012)

---

*ADR aprobado por MYSTIC — Deployed to production 2026-08-23*