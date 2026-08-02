# ADR-20260729-VOICE-SERVICE — Voice Service Unificado

## Context

Actualmente existen 5 pipelines de voz fragmentados:
1. WhatsApp responder (whatsapp_agent.py) — edge-tts + ffmpeg propio
2. JARVIS assistant (assistant.py) — OpenAI TTS
3. Aztrotech (tts-server.py) — edge-tts CLI
4. Content Studio (edge-tts-server.py) — edge-tts con FastAPI
5. Clon Digital (fal-wrapper) — FAL.ai seed-audio

Cada uno maneja sanitización, chunking, formato y errores de forma distinta. Agregar un nuevo canal requiere replicar lógica.

## Decision

Construir un `voice-service` HTTP centralizado que cualquier canal/agente MCP pueda consumir via REST. 90-95% open-source.

## Options Considered

| Opción | Ventajas | Desventajas |
|--------|----------|-------------|
| **Voice Service unificado** | Un solo endpoint, lógica compartida, caché central, fácil de testear | Punto único de falla (mitigable con health check) |
| Mantener pipelines separados | Sin refactor | 5x código, 5x bugs, 5x mantenimiento |
| Usar servicio cloud (ElevenLabs API directa) | 0 código | Vendor lock-in, costo recurrente, sin fallback local |
| Usar OpenClaw voice plugin | Ya existe | Dependencia de OpenClaw, menos control |

## Consequences

- **Positivo**: Nuevos canales solo POSTean texto, reciben audio. Caché reduce costos de API. edge-tts funciona sin GPU.
- **Negativo**: Single point of failure si el servicio cae (mitigado por health check + auto-restart systemd).
- **Riesgo**: edge-tts puede tener latencia variable en CPU de laptop. Mitigación: timeout de 10s + fallback cloud.

## Lessons

Los pipelines anteriores demostraron que edge-tts funciona bien en CPU para frases de <500 chars. El problema actual no es TTS, es que cada pipeline reinventa el wrapping.

## Related

- SPEC-20260729-VOICE-SERVICE
- ADR-20260718-CLONE-SERVICE (clon digital voice pipeline)
