---
name: deploy-voice
description: >
  Activa el pipeline de voz para un cliente.
  Configura STT (Whisper/Deepgram/OpenAI), TTS (OpenAI/ElevenLabs/OpenVoice),
  wake word, y expone via WebSocket.
license: MIT
compatibility: opencode
metadata:
  domain: voice
  capabilities: stt, tts, wake-word, channels
---

## Qué hace

Toma la config de un cliente y activa su asistente de voz:
- Selecciona proveedor STT (Whisper local, Deepgram, OpenAI)
- Selecciona proveedor TTS (OpenAI, ElevenLabs, OpenVoice)
- Configura wake word personalizada
- Conecta canales (web, telegram, whatsapp)
- Expone vía WebSocket en ABE Service

## Cuándo usarlo

- Cuando un nuevo cliente contrata Voice Assistant
- Cuando un artista quiere su propio asistente
- Cuando se cambia de proveedor STT/TTS

## Pasos

1. **Leer config del cliente**
   - Lee clients/<nombre>/config.yml
   - Identifica: stt_provider, tts_provider, wake_word, language, channels

2. **Configurar STT**
   - whisper: verificar que el modelo base está descargado
   - deepgram: configurar API key
   - openai: configurar API key
   - Probar: transcribir un audio de prueba

3. **Configurar TTS**
   - openai: configurar voice_id (alloy, nova, etc.)
   - elevenlabs: configurar API key + voice_id
   - openvoice: verificar que el container omnivoice corre en :3900
   - Probar: generar audio de prueba

4. **Configurar wake word**
   - Crear perfil de wake word: "Hey <nombre_asistente>"
   - Configurar sensibilidad

5. **Conectar canales**
   - web: exponer endpoint /api/voice/ws
   - telegram: conectar al bot existente
   - whatsapp: conectar al bridge

6. **Probar flujo completo**
   - Wake word -> STT -> procesar -> TTS -> respuesta

## Referencias

- STT: src/voice/stt.py
- TTS: src/voice/tts.py
- ABE Service voice endpoints: apps/abe_service/core/voice_pipeline.py
