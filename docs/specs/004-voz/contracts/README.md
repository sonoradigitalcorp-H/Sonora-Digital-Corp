# Contracts: Voz
**Spec**: spec.md
---
## API Contracts
- `POST /api/voice/transcribe` — Transcribir audio a texto
- `POST /api/voice/speak` — Generar audio desde texto
- `POST /api/voice/detect-wake` — Detectar wake word
- `GET /api/voice/status` — Estado del módulo de voz
## Data Contracts
```json
{ "transcription": { "text": "string", "confidence": "float", "language": "string" } }
{ "tts_request": { "text": "string", "lang": "es-MX", "voice": "string" } }
```
