# ADR-20260802-AZROTECH-VOZ-LOCAL

| Campo | Valor |
|-------|-------|
| **ID** | `ADR-20260802-AZROTECH-VOZ-LOCAL` |
| **Fecha** | 2026-08-02 |
| **Spec** | Fase 3 Voz (TICKET-011..013) |
| **Estado** | aceptado |

---

## Context

AstroTech quiere conversación por voz: el cliente manda nota de voz y el bot responde con audio. Existía un `tts-server.py` (edge-tts, puerto 8765) que NO corría, el STT usaba Google `speech_recognition` (online, sin pasar por el engine RAG-first), y había referencias a FreeSWITCH (inactivo, sin SIP trunk), Qwen3-TTS y Kokoro/clonación de voz. RAM del equipo: **3.3GB total, ~645MB libres** con el bot corriendo.

## Decision

**Confirmada por César**: voz **100% local** con:
- **TTS**: `edge-tts` (gratuito, Microsoft Neural) con voz **`es-MX-DaliaNeural`** en `tts-server.py` (puerto 8765).
- **STT**: `faster-whisper` modelo **`small`** (idioma español, 16kHz mono) en nuevo módulo `bot/stt_local.py`.

Flujo: audio entrante → ffmpeg a 16kHz → STT local → `ConversationEngine.process` (mismo pipeline RAG-first que texto) → TTS local `es-MX-DaliaNeural` → OGG opus → respuesta de audio. Modelo whisper se carga en `post_init`.

Se descartan para esta fase: FreeSWITCH (infra telefónica), Qwen3-TTS y Kokoro/clonación real de la voz de César (RAM insuficiente sin sacrificar whisper; queda como fase futura).

## Options Considered

| Opción | Pros | Contras |
|--------|------|---------|
| **edge-tts + faster-whisper small (local)** | 100% gratis y offline, RAM acotada | Voz clon no es la de César, latencia CPU |
| Qwen3-TTS (clon de César) | Voz real del dueño | RAM insuficiente con whisper |
| Kokoro TTS (clon) | Ligero, voice clone | Calidad menor, setup extra |
| FreeSWITCH + SIP trunk | Telefonía real | Inactivo, sin trunk, fuera de alcance MVP |
| Google speech_recognition (STT) | Sin modelo local | Online, dependencia externa, sin engine |

## Consequences

- **Positivas**: conversación por voz offline, costo $0, mismo pipeline de contexto/memoria/leads que texto.
- **Positivas**: edge-tts ya está instalado (7.2.8) y `faster-whisper` (1.2.1) + `torch 2.5.1+cpu` disponibles.
- **Trade-off**: la voz no es la clonada de César (es DaliaNeural); para voz de César real hace falta una fase con más recursos o streaming.
- **Config**: se añade sección `voice.stt`/`voice.tts`; `audio_first.tts_voice: es-MX-DaliaNeural`.

## Lessons

- `es-MX-JorgeNeural` (masculino) era la voz por defecto del tts-server; se cambia a `es-MX-DaliaNeural` por decisión del dueño.
- El TTS server usa subproceso `edge-tts` y `ffmpeg`; verificar que ambos estén en PATH antes de arrancar.
- La carga de whisper `small` (~500MB) debe ser lazy en `post_init` para no bloquear el polling del bot.

## Related

- Spec: TICKET-011..013
- Events: `tts-server.py`, `bot/stt_local.py`, `config.yaml`
