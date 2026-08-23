# Spec SDD 0012 — Web Chat Pro Max + Voz 24/7 en VPS OVH

**ID**: 0012-web-chat-voice-redesign
**Version**: 1.0.0
**Date**: 2026-08-22
**Author**: MYSTIC / SDC
**Status**: EN IMPLEMENTACIÓN

## Resumen

Rediseño COMPLETO de la presencia web: chat + voz en sonoradigitalcorp.com y subdominios,
todo el cómputo pesado (STT/TTS/LLM) corriendo en VPS OVH `149.56.46.173`. UI nueva:
Three.js orbe reactivo + glassmorphism, sin dashboard, sin signos de exclamación.
Vender BENEFICIOS (tiempo, dinero, tranquilidad), nunca tecnología.

## Constitution Check

### Principio I: Orquestación Única
- [x] Web → nginx VPS → vps_ai_server.py :8643 → OpenRouter (deepseek-0731 → nemotron fallback)
- [x] Voz → nginx VPS → voice servers (:5292 STT, :5293 TTS) — procesos systemd con Restart=always
- [x] Hermes gateway :8642 NO se toca (solo bots/canales)

### Principio II: Separación Determinista vs LLM
- [x] Routing tenant (persona sdc|nathaly): determinista por endpoint/path
- [x] Lead scoring: determinista (`lead_scoring.py` existente)
- [x] Onboarding: motor determinista (`onboarding_hermosillo.py`) + LLM solo conversación
- [x] Respuesta conversacional: LLM con system prompt SOUL (sin exclamaciones)

### Principio III: Cargas pesadas SOLO en VPS (regla de oro)
- [x] faster-whisper small int8 → VPS :5292 (CPU VPS, no laptop)
- [x] Kokoro TTS es-MX → VPS :5293; fallback edge-tts (red, $0)
- [x] Laptop: cero procesos nuevos

### Principio IV: Testing
- [x] Tests unitarios pipeline voz (STT/TTS roundtrip)
- [x] Tests eval prompts (juez nemotron-free)
- [x] Test E2E Playwright: texto→respuesta, mic→voz→texto→voz respuesta

### Principio V: Trazabilidad
- [x] Cada conversación → SQLite leads/conversaciones (ya existe)
- [x] Métricas latencia en logs JSON del ai_server

## Spec

### Inputs
| Canal | Formato | Destino |
|-------|---------|---------|
| Chat web | POST `/api/v1/chat/completions` {messages[], model?, person?} | vps_ai_server :8643 |
| Voz usuario | POST `/api/stt` multipart audio (webm/ogg/mp3, ≤60s) | stt_server :5292 |
| Mic streaming | MediaRecorder chunks → POST por turno (push-to-talk) | mismo |

### Outputs
| Acción | Formato | SLA |
|--------|---------|-----|
| Texto respuesta | SSE stream o JSON completo | primer byte <1.5s p95 |
| Voz respuesta | GET `/api/tts?text=` → audio/mpeg stream | first-byte <800ms |
| Roundtrip voz | hablas → responden en voz | <4s p95 |
| Lead capturado | SQLite + notificación dueño | <30s |

### Contratos API (nuevos)
```
POST /api/stt            multipart: file=@audio.webm  → {text, lang, duration_s}
GET  /api/tts?text=&voice=&person=  → audio/mpeg (stream)
POST /api/v1/chat/completions       {messages, person} → OpenAI-compatible JSON
GET  /health                        → {status, services:{llm,stt,tts}}
```

person ∈ {"sdc","nathaly"} — system prompt SOUL inyectado server-side (determinista).

### Soul (identidad de voz — regla dura)
- CERO signos de admiración (¡!) ni interrogación agresiva en copy visible ni TTS.
  Preguntas suaves permitidas con "¿" normal pero tono afirmativo.
- Frases cortas. Tono: tranquilo, seguro, cercano. Español MX neutro.
- PROHIBIDO decir: IA, agente, modelo, LLM, token, prompt, RAG, embedding, chatbot, bot.
- DECIR: asistente, te ayudo, tu negocio, tu tiempo, resultados, tranquilidad.
- Vendemos: tiempo libre, cero multas, más clientes, control, crecimiento.

### UI Pro Max (requisitos duros)
1. Three.js orbe 3D reactivo: amplitud del audio de respuesta escala/color del orbe.
   Partículas GPU (BufferGeometry + PointsMaterial), shaders custom GLSL.
2. Glassmorphism: paneles `backdrop-filter: blur(24px) saturate(140%)`,
   borde 1px rgba(255,255,255,.18), sombra profunda, fondo canvas animado.
3. Chat render: burbujas glass, streaming de tokens, auto-scroll suave, 60fps.
4. Micrófono: push-to-talk (click para hablar/click para enviar), visualizador nivel.
5. Altavoz: reproduce /api/tts, botón STOP siempre visible mientras habla.
6. SIN dashboard, SIN panel admin, SIN métricas visibles. Solo valor.
7. Mobile-first: funciona sin hover, tap targets ≥48px.

### Copy (beneficios primero)
- Hero SDC: "Tu empresa atendiendo sola las 24 horas. Tú dedícate a crecer."
- Hero Nathaly: "Tu contabilidad en orden y tu tiempo de vuelta."
- CTAs: "Quiero mi diagnóstico gratis" / "Hablar ahora"
- Muestras de valor: números de resultado ("+16 horas al mes de vuelta",
  "cero multas SAT", "responde en segundos a cualquier hora") — nunca features técnicas.

## Plan de Implementación

### Fase A (hoy): Voice servers VPS
1. `voice/stt_server.py` — aiohttp :5292, faster-whisper small int8, warm-up al inicio.
2. `voice/tts_server.py` — aiohttp :5293, kokoro-onnx si disponible; SIEMPRE fallback edge-tts.
3. Extender `vps_ai_server.py`: montar sub-apps STT/TTS + health agregado.
4. Deploy rsync → systemd units `sdc-stt.service`, `sdc-tts.service`, restart `vps-ai-server`.

### Fase B (hoy): UI Pro Max
5. `chat_pro_max/index.html` — un solo archivo: Three.js orb + glass + chat + voz.
   Personas: `?p=nathaly` rebrandea todo (nombre, colores, hero).
6. Deploy a `/var/www/sonoradigitalcorp/` vía nginx VPS.

### Fase C: Agents + soul
7. `SOUL.md` canónico en repo + copia a ~/.hermes/SOUL.md y agentes activos.
8. Eval prompts: `prompt_registry/eval_prompts.yaml` + `run_eval.py` (juez nemotron free).

### Fase D: Tests + E2E
9. pytest local: clean_for_tts sin exclamaciones, scoring, onboarding.
10. E2E Playwright contra https://sonoradigitalcorp.com (post-deploy).

## Criterios de Éxito
- [ ] /health en VPS reporta llm+stt+tts OK
- [ ] Hablar al mic → respuesta hablada < 4s p95 desde Hermosillo
- [ ] Orbe reacciona al volumen del audio de respuesta (visible a simple vista)
- [ ] 0 signos de exclamación en respuestas (test automatizado sobre 20 respuestas)
- [ ] Copy sin palabras prohibidas (test grep)
- [ ] Sin dashboard en la página
- [ ] systemd: 6 servicios VPS activos con Restart=always

## Riesgos
| Riesgo | Mitigación |
|--------|------------|
| RAM VPS limitada (11GB) con whisper+kokoro | small int8 (~500MB) + kokoro onnx (~400MB); si presión: tiny int8 |
| Kokoro es-MX calidad | edge-tts DaliaNeural como default hasta validar kokoro |
| Navegadores sin MediaRecorder | Fallback: input texto siempre visible |
| Latencia red MX→OVH | keep-alive HTTP, audio opus 24k, respuestas ≤500 chars |
