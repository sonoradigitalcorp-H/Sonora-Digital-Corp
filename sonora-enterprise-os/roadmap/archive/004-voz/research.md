# Research: Voz STT/TTS
**Spec**: spec.md
---
## Tecnologías Evaluadas
| Opción | Ventajas | Desventajas | Decisión |
|--------|----------|-------------|----------|
| faster-whisper (base.int8) | Local, gratis, CPU eficiente, VAD | ~85% accuracy en español | ✅ STT principal |
| edge-tts | Gratis, voces naturales, español | Requiere internet | ✅ TTS principal |
| gTTS | Gratis, simple | Voz robótica | ✅ Fallback TTS |
| ElevenLabs | Voz ultra-realista | Costo, API key | ⏸️ Skill OpenClaw |
## Decisión Arquitectónica
- **Selección**: faster-whisper → edge-tts → gTTS → espeak (cascada)
- **Motivo**: Sin depender de APIs externas para funcionamiento básico
## Limitaciones
1. Whisper base tiene ~85% accuracy en español con ruido
2. edge-tts requiere conexión a internet
