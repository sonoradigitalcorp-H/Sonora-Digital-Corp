# SPEC — Voice Service Unificado

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260729-VOICE-SERVICE` |
| **Fecha** | 2026-07-29 |
| **Autor** | Luis Daniel Guerrero Enciso / Mystic |
| **Tier** | 1 |
| **Estado** | borrador |
| **Score requerido** | ≥60 |

---

## 1. Objetivo

Unificar los 5 pipelines de voz fragmentados (WhatsApp, Telegram, Twilio, JARVIS local, Aztrotech) en un solo `voice-service` HTTP que cualquier canal o agente MCP pueda llamar para generar audio a partir de texto. 90-95% open-source (edge-tts + ffmpeg + Python stdlib), solo APIs cloud para STT/TTS premium (ElevenLabs, fal.ai, OpenAI).

---

## 2. Value Driver

`automation` / `founder-independence` — elimina la fragmentación actual (5 pipelines separados, 4 implementaciones TTS distintas, formatos inconsistentes). Cada nuevo canal solo necesita POSTear texto al voice-service y recibe audio listo para entregar.

---

## 3. Functional Requirements

| FR# | Descripción | Prioridad |
|-----|-------------|-----------|
| FR1 | Sanitizar texto de entrada (quitar markdown, HTML, emojis, código) antes de TTS | P1 |
| FR2 | Dividir texto largo en chunks de ≤1000 caracteres con corte por oración | P1 |
| FR3 | Seleccionar voz según tenant + idioma + canal (registro configurable) | P1 |
| FR4 | Generar TTS con edge-tts (local, CPU, gratis) como motor default | P1 |
| FR5 | Fallback a ElevenLabs / OpenAI TTS si edge-tts falla | P2 |
| FR6 | Normalizar volumen con loudnorm de ffmpeg | P2 |
| FR7 | Convertir a formato destino (OGG Opus 16kHz para WA, MP3 para web, WAV 8kHz para Twilio) | P1 |
| FR8 | Cachear respuesta por hash MD5(texto + voz + idioma) para no regenerar | P1 |
| FR9 | Validar audio generado (duración > 0, archivo no corrupto) | P1 |
| FR10 | Registrar métricas: costo, latency, modelo usado, tenant | P2 |
| FR11 | Exponer health check endpoint | P1 |
| FR12 | Exponer endpoint para listar voces disponibles por tenant | P1 |

---

## 4. Success Criteria

- [ ] TTS pipeline completo funciona con edge-tts en CPU < 2s por frase de 200 chars
- [ ] Los 3 formatos de salida (OGG, MP3, WAV) se generan correctamente
- [ ] Cache devuelve audio en < 10ms para requests repetidos
- [ ] Texto con markdown se sanitiza correctamente (no se leen asteriscos en voz alta)
- [ ] Texto de 3000 chars se divide en 3 chunks y se concatenan en un solo audio
- [ ] Fallback a ElevenLabs funciona cuando edge-tts falla
- [ ] Cobertura de tests ≥ 80%

---

## 5. Gherkin Scenarios

Ver `tests/gherkin/feature-*.feature` (9 features, ~36 scenarios)

---

## 6. Edge Cases

- [EC1] Texto vacío → error 400 con mensaje claro
- [EC2] Texto con solo emojis → sanitize devuelve string vacío → error 400
- [EC3] Texto con código HTML/XML → se escapa o elimina
- [EC4] Tenant sin voz configurada → usar voz default del sistema
- [EC5] edge-tts falla (timeout, proceso muerto) → fallback automático a ElevenLabs
- [EC6] Audio generado de 0 bytes → retry con fallback, si persiste → error 500
- [EC7] Chunking parte una palabra en medio de una oración → cortar por punto, signo, o espacio
- [EC8] Request concurrente del mismo texto+voz → cache previene doble generación

---

## 7. Technical Approach

```
POST /v1/tts
{
  "text": "string",
  "tenant": "string (opcional)",
  "voice": "string (opcional)",
  "language": "es|en (default: es)",
  "format": "ogg|mp3|wav (default: ogg)"
}

Response 200:
{
  "audio_url": "/v1/audio/{hash}.ogg",
  "format": "ogg",
  "duration_ms": 3200,
  "model": "edge-tts",
  "voice": "es-MX-DaliaNeural",
  "cached": true
}
```

Arquitectura: FastAPI + edge-tts + ffmpeg subprocess. Cache en disco (`data/cache/`). Sin dependencias GPU. Sin Java. Sin Node.

Archivos:
- `api/server.py` — FastAPI endpoints
- `core/sanitize.py` — limpieza de texto
- `core/chunk.py` — división inteligente
- `core/voice.py` — selección de voz por tenant
- `core/tts.py` — edge-tts wrapper
- `core/postprocess.py` — ffmpeg formatos y normalización
- `core/cache.py` — caché por hash
- `core/validate.py` — validación de audio
- `core/metrics.py` — registro de costos y métricas
- `config/voices.yaml` — registro de voces por tenant
- `requirements.txt` — solo Python stdlib + edge-tts + fastapi + uvicorn

---

## 8. Dependencies

- `edge-tts` (MIT) — TTS local, CPU, 0 dependencias externas
- `ffmpeg` (LGPL) — conversión de formatos
- `fastapi` + `uvicorn` (MIT) — servidor HTTP
- Opcional: `openai` (API) — fallback TTS
- Opcional: `httpx` — ElevenLabs API
- **Sin GPU, sin Java, sin Node, sin Docker obligatorio**

---

## 9. Events to Emit

| Evento | Cuándo |
|--------|--------|
| `voice:tts:generated` | Audio generado exitosamente |
| `voice:tts:failed` | Error de generación después de retry |
| `voice:tts:fallback` | Se usó fallback porque primary falló |
| `voice:tts:from-cache` | Audio servido desde caché |

---

## 10. Kill Criteria

- edge-tts no puede correr sin GPU en esta laptop (< 5s por frase)
- ffmpeg no está disponible en el sistema
- El caching no reduce el tiempo de generación significativamente

---

## 11. Scale Criteria

- Cuando haya >5 tenants concurrentes, migrar a contenedor Docker
- Cuando el caché supere 1GB, añadir TTL y limpieza programada
- Cuando se necesiten >10 voces distintas, migrar registro a JSON en Redis
