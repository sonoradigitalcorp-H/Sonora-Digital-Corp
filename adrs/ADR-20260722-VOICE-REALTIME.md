# ADR-20260722-VOICE-REALTIME
# Sistema de Voz en Tiempo Real Mystic

**Estado**: Aceptado
**Fecha**: 2026-07-22
**Spec Relacionada**: SPEC pendiente

## Contexto

Mystic, el alma de Sonora Digital Corp, necesita un sistema de voz en tiempo real que:
1. Procese voz con latencia mínima (WebSocket streaming)
2. Ofrezca templates de respuesta dinámicos y variados
3. Incluya música de fondo / soundscapes envolventes
4. Enrute al usuario a donde solicita (calendario, precios, contacto)
5. Funcione como "obra de arte" interactiva con identidad visual única

El sistema existente (`clients/aztrotech/realtime_voice/`) resolvía parte del problema pero era específico para AztroTech, sin templates, sin soundscapes, sin routing inteligente.

## Decisión

Se crea `apps/voice-realtime/` como pipeline canónico de voz para Mystic, con:

### Arquitectura

```
Frontend (HTML+JS+Audio) 
    ↕ WebSocket (PCM16 base64)
Server (FastAPI + WebSocket)
    ├── VAD (Voice Activity Detection)
    ├── Whisper STT (transcripción)
    ├── Intent Router (clasificación + routing)
    ├── Voice Templates (respuestas variadas)
    ├── LLM (OpenRouter, fallback)
    ├── TTS Engine (Edge / OmniVoice / OpenAI)
    ├── Audio Mixer (TTS + Soundscape)
    └── Soundscape Generator (5 ambientes)
```

### Componentes Clave

| Componente | Archivo | Función |
|------------|---------|---------|
| Servidor WebSocket | `server.py` | Orquestación completa del pipeline |
| STT Streaming | `pipeline/stt.py` | Whisper + VAD (detección de silencio) |
| TTS con fallback | `pipeline/tts.py` | Edge → OmniVoice → OpenAI |
| Audio Mixer | `pipeline/audio_mixer.py` | Mezcla TTS + soundscape con ducking |
| Intent Router | `intent_router.py` | Regex + LLM fallback, 12 intenciones |
| Voice Templates | `voice_templates.py` | 8 categorías, variantes aleatorias sin repetición |
| Frontend | `frontend/mystic_voice.html` | Orb visual, soundscapes, mic, redirect |

### Protocolo (OpenAI Realtime compatible extendido)

Mensajes estándar: `session.created`, `conversation.item.created`, `response.output_text.delta`, `response.audio.delta`, `response.done`

Extensiones Mystic:
- `soundscape.delta` — audio de fondo (PCM16, loop continuo)
- `soundscape.changed` — confirmación de cambio de ambiente
- `redirect` — comando para redirigir navegador a URL
- `change_soundscape` — solicitud de cambio de ambiente
- `change_tone` — solicitud de cambio de tono de voz

### Soundscapes

5 ambientes sintéticos generados con síntesis de audio puro (sin archivos):
- Minimal (pad suspendido, fondo neutro)
- Naturaleza (viento + agua, relajante)
- Cálido (bajos + acorde mayor, acogedor)
- Futurista (pad barrido + arpegios, tecnológico)
- Energético (beat 90BPM + bajo walking, activo)

### Routing por Intención

El Intent Router clasifica 12 intenciones con:
1. Regex rápido (patrones por intención)
2. LLM fallback (vía mem_sabe para casos complejos)
3. Confianza >50% para activar routing

Destinos: calendario (`calendario.sonoradigitalcorp.com`), precios (`/#pricing`), servicios (`/#features`), contacto (WhatsApp), productos específicos.

## Opciones Consideradas

1. **OpenAI Realtime API**: Dependencia externa, costo por minuto, sin control de soundscapes
2. **Twilio Voice**: Enfocado en llamadas telefónicas, no en experiencia web inmersiva
3. **WebSocket propio con Whisper local**: Control total, sin costos recurrentes de STT/TTS, extensible

Se eligió la opción 3 por: cero dependencias externas (excepto LLM opcional), control total de la experiencia, soundscapes personalizados, routing inteligente.

## Consecuencias

### Positivas
- Experiencia unificada de voz en todos los canales
- Mystic puede redirigir usuarios a destinos específicos por voz
- Soundscapes dan identidad y calidez a la interacción
- Templates evitan respuestas robóticas
- Sin costos de API de voz (Whisper + Edge TTS son locales/gratuitos)

### Negativas
- Whisper base requiere ~1GB RAM para el modelo
- Edge TTS necesita conexión a internet (Azure Cognitive Services)
- Soundscapes sintéticos no reemplazan audio real grabado

## Lecciones

- El VAD con umbral RMS simple funciona para entornos silenciosos pero necesita mejora para ruido ambiental
- Los templates funcionan mejor cuando el LLM los complementa, no los reemplaza
- El ducking de audio (bajar volumen de fondo al hablar) es crucial para la claridad

## Métricas de Éxito

- Latencia total <2s (STT→LLM→TTS)
- Precisión de intent routing >80%
- Usuarios completan acción (redirect) >40%
- Sin errores de conexión WebSocket >95% sesiones
