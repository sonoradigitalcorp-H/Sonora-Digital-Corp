# Feature Specification: Voz

**Feature**: 004-voz
**Status**: Active
**Input**: JARVIS necesita interfaz de voz completa: reconocimiento de voz (STT), síntesis de voz (TTS) y detección de wake word para activación por manos libres.

---

## User Stories

### US9 — Comandos por voz (push-to-talk)
El usuario habla y JARVIS transcribe el audio a texto, procesa el comando, y responde por voz.

**Prioridad**: P1
**Dependencias**: Ninguna

**Independent Test**: Enviar un archivo de audio de prueba al endpoint `/api/voice/transcribe`, verificar que devuelve texto transcrito. Testeable con Whisper funcionando.

**Acceptance Scenarios**:
1. **Given** el usuario presiona el botón de voz en la UI, **When** habla y suelta, **Then** el audio se transcribe a texto y se envía como mensaje.
2. **Given** JARVIS genera una respuesta, **When** la respuesta está completa, **Then** se reproduce en voz alta mediante TTS.
3. **Given** que Whisper no está disponible, **When** el usuario intenta usar STT, **Then** fallback a Google STT o Sphinx.

### US10 — Wake word para activación manos libres
El usuario dice "Hey JARVIS" y el sistema comienza a escuchar sin necesidad de interacción manual.

**Prioridad**: P2
**Dependencias**: US9

**Independent Test**: Ejecutar el detector de wake word con un archivo de audio que contenga "Hey JARVIS", verificar que lo detecta. Testeable sin micrófono ni interfaz gráfica.

**Acceptance Scenarios**:
1. **Given** el sistema en reposo, **When** el usuario dice "Hey JARVIS", **Then** el sistema activa el modo escucha.
2. **Given** variantes como "Oye JARVIS" o "Hey Jarv", **When** el usuario las dice, **Then** también activan el modo escucha.
3. **Given** el wake word detectado, **When** pasan 2 segundos sin actividad, **Then** el sistema vuelve a reposo.

---

### Edge Cases

- ¿Qué pasa si Whisper no está instalado? El sistema MUST fallback a Google STT o Sphinx.
- ¿Qué pasa si no hay micrófono disponible? El sistema MUST deshabilitar STT con mensaje claro.
- ¿Qué pasa si el audio es demasiado largo (> 30s)? El sistema MUST truncar o chunkear el audio.
- ¿Qué pasa si edge-tts falla por falta de red? El sistema MUST fallback a gTTS o espeak.
- ¿Qué pasa si hay ruido de fondo excesivo? El sistema MUST notificar baja calidad de audio.
- ¿Qué pasa si el wake word se detecta mientras ya se está procesando un comando? El sistema MUST ignorar wake words duplicadas hasta que termine el ciclo actual.

---

## Requirements

### Functional Requirements

**FR-030**: El sistema MUST transcribir audio a texto usando Whisper (faster-whisper) con fallback a Google STT y Sphinx.
**FR-031**: El sistema MUST sintetizar texto a voz usando edge-tts con fallback a gTTS y espeak.
**FR-032**: El sistema MUST detectar wake word "Hey JARVIS" (y variantes) mediante regex.
**FR-033**: El sistema MUST mantener una cola de TTS con prioridad e interrupción.
**FR-034**: El VoiceAgent (orquestador) MUST gestionar sesiones de voz (start, process audio, end, status).
**FR-035**: El sistema MUST exponer APIs REST: `/api/voice/transcribe`, `/api/voice/speak`, `/api/voice/detect-wake`, `/api/voice/status`.

### Key Entities

- **Wake Word**: Frase que activa el modo escucha ("Hey JARVIS", "Oye JARVIS", "Hey Jarv").
- **STT Engine**: Motor de reconocimiento de voz (Whisper primario, Google/Sphinx fallback).
- **TTS Engine**: Motor de síntesis de voz (edge-tts primario, gTTS/espeak fallback).

---

## Success Criteria

- **SC-030**: Transcripción de audio < 5s para 10s de audio.
- **SC-031**: TTS genera audio < 3s para 100 caracteres de texto.
- **SC-032**: Wake word detecta correctamente en 3 de 3 intentos, con 0 falsos positivos en 1 minuto de silencio.
- **SC-033**: VoiceAgent start/process/end session funciona sin errores.

---

## Assumptions

- Whisper model corre localmente (CPU, int8 quantization).
- edge-tts requiere conexión a internet (fallback a gTTS local).
- Web Speech API disponible en el navegador para STT/TTS desde la UI.
