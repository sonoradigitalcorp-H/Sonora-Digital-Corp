# Voz en Tiempo Real — AztroTech

Arquitectura para llamadas de voz en tiempo real vía web.
Sin Twilio, sin HF, sin dependencias externas de terceros.

## Arquitectura

```
[Browser] ←→ WebSocket (PCM16 16kHz) ←→ [WebSocket Server]
                                             ├── Whisper STT (local)
                                             ├── Mystic LLM (OpenRouter)
                                             └── Qwen3-TTS (voz clonada de César)
```

### Pipeline de audio

```
Micrófono → getUserMedia (48kHz Float32)
         → AudioWorklet (resample → 16kHz Int16 PCM)
         → WebSocket (base64 chunks cada ~40ms)
         → Servidor:
             1. Whisper STT          → transcripción
             2. Mystic (OpenRouter)  → respuesta textual
             3. Qwen3-TTS (voz César) → audio 24kHz PCM
         → WebSocket (response.output_audio.delta)
         → AudioWorklet (resample → 48kHz Float32)
         → Altavoz
```

### Barge-in (interrupción)

Cuando el usuario habla mientras el asistente está respondiendo:
- El VAD del servidor detecta speech_started
- Cliente limpia el buffer de playback
- El servidor cancela la respuesta en curso
- El reconocimiento continúa en el nuevo input

## Componentes

| Componente | Archivo | Función |
|-----------|---------|---------|
| WebSocket Server | `server.py` | FastAPI + WebSocket, orquesta pipeline |
| STT | `pipeline/stt.py` | Whisper base (local), transcripción |
| LLM | `pipeline/llm.py` | OpenRouter con Mystic persona |
| TTS | `pipeline/tts.py` | Qwen3-TTS con voz clonada de César |
| Frontend | `frontend/` | HTML+JS, orb, micrófono, WebSocket |
| Limiter | `limiter.py` | Control de uso diario (SQLite) |

## Tecnologías

- **Transporte**: WebSocket (TCP) — funciona en redes corporativas y móviles
- **STT**: Whisper base (openai-whisper, local, ~500ms)
- **LLM**: OpenRouter (`nvidia/nemotron-3-nano-30b-a3b:free`)
- **TTS**: Qwen3-TTS-12Hz-0.6B-Base con voz clonada de César
- **Frontend**: HTML+JS vanilla, AudioWorklet, canvas orb
- **Servidor**: FastAPI + uvicorn

## Protocolo (OpenAI Realtime GA)

Basado en el protocolo que usa HF Realtime Voice:

```
Cliente → Servidor:
  session.update: {output_modalities: ["audio"], voice, instructions}
  input_audio_buffer.append: {audio: "base64 PCM16 16kHz"}
  input_audio_buffer.commit
  response.create

Servidor → Cliente:
  session.created
  input_audio_buffer.speech_started
  input_audio_buffer.speech_stopped
  response.output_audio.delta: {delta: "base64 PCM16 24kHz"}
  response.output_audio.done
  response.done
```

## Implementación por fases

### Fase 1 — Servidor WebSocket básico (branch: feat/ws-server)
- [ ] Servidor FastAPI con WebSocket en `/v1/realtime`
- [ ] Recepción de chunks de audio base64
- [ ] Whisper STT → transcripción a texto
- [ ] Logging de transcripciones

### Fase 2 — Pipeline Mystic (branch: feat/ws-llm)
- [ ] Conexión con OpenRouter usando Mystic persona
- [ ] Historial de conversación por sesión
- [ ] Streaming de respuesta textual

### Fase 3 — TTS con voz de César (branch: feat/ws-tts)
- [ ] Instalar Qwen3-TTS desde Hugging Face
- [ ] Clonar voz de César con el audio de 2:46
- [ ] Conversión texto → audio → base64 → WebSocket
- [ ] Barge-in con VAD

### Fase 4 — Frontend web (branch: feat/ws-frontend)
- [ ] Página web con micrófono (getUserMedia)
- [ ] AudioWorklet para resample 48→16kHz
- [ ] WebSocket client con reconexión automática
- [ ] Orb visualizador (canvas, reactivo a audio)
- [ ] Historial de conversación

### Fase 5 — Producción (branch: feat/ws-prod)
- [ ] Dockerizar servidor
- [ ] Systemd service
- [ ] SSL/HTTPS con Let's Encrypt
- [ ] Integrar en `calendario.sonoradigitalcorp.com`
- [ ] Rate limiting por IP
- [ ] Monitoreo y logging

## Recursos
- HF Realtime Voice: https://huggingface.co/spaces/smolagents/hf-realtime-voice
- Qwen3-TTS: https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-Base
- Protocolo: https://platform.openai.com/docs/guides/realtime
