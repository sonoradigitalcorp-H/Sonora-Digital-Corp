# Data Model: Voz
**Spec**: spec.md
---
## Entidades
| Entidad | Atributos | Descripción |
|---------|-----------|-------------|
| AudioChunk | id, data, sample_rate, format, duration | Fragmento de audio |
| Transcription | text, confidence, language, duration | Texto transcrito |
| VoiceSession | id, mode, messages[], active | Sesión de voz activa |
| WakeWord | text, threshold, cooldown | Palabra de activación |
## Relaciones
```
(AudioChunk)-[:TRANSCRIBED_TO]->(Transcription)
(VoiceSession)-[:CONTAINS]->(AudioChunk)
```
