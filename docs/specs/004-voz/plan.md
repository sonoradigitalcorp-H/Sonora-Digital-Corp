# Implementation Plan: Voz

**Spec**: [spec.md](./spec.md)

---

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: faster-whisper, SpeechRecognition, edge-tts, gTTS, pyttsx3/espeak, pyaudio
**Architecture**: Módulo Python `voice/` con cuatro submódulos + integración web via Web Speech API
**Testing**: pytest con mocking de audio y APIs externas

## Constitution Check

| Principio | Cómo lo cumple |
|-----------|---------------|
| Privacidad y control | Whisper local, wake word local sin cloud |
| Arquitectura modular | STT, TTS y wake word son módulos independientes |
| Calidad y testing | Tests con mocking de microfono y APIs |

## Implementación

### Archivos existentes

| Archivo | Propósito |
|---------|-----------|
| `voice/__init__.py` | Exports públicos |
| `voice/stt.py` | Whisper STT + VAD filter + fallback chain (Google, Sphinx) |
| `voice/tts.py` | Multi-engine TTS + queue + priority + interruption + callbacks |
| `voice/wake_word.py` | Regex wake word + cooldown + background listening |
| `voice/cli.py` | CLI utility (mic, transcribe, speak, wake, listen) |
| `webui/fastapp.py` | APIs REST voice (/transcribe, /speak, /detect-wake, /status) |
| `webui/static/app.js` | Web Speech API integration (webkitSpeechRecognition, speechSynthesis) |
| `src/core/orchestrator.py` | VoiceAgent (transcribe, speak, sessions, status) |

### Pendiente

| Tarea | Prioridad |
|-------|-----------|
| Volume meter visual en UI | P2 |
| Settings panel (selección de micrófono, velocidad TTS) | P2 |
| Tests para STT y TTS (hoy solo hay tests de wake word y TTS engine) | P2 |

## Archivos del spec

```
specs.new/004-voz/
├── spec.md
├── plan.md
└── tasks.md
```
