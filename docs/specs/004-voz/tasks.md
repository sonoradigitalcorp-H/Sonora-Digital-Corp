# Tasks: Voz

---

## US9 — Comandos por voz (P1)

- [x] Implementar `voice/stt.py` (Whisper + VAD + fallbacks)
- [x] Implementar `voice/tts.py` (edge-tts + gTTS + espeak + queue + priority + interruption)
- [x] Implementar `voice/__init__.py` con exports limpios
- [x] APIs REST en `webui/fastapp.py` (transcribe, speak, status)
- [x] Web Speech API integration en `app.js` (webkitSpeechRecognition, speechSynthesis)
- [x] Botón de voz en UI con estados (idle, listening, processing)
- [x] VoiceAgent en orquestador (transcribe, speak, sessions, status)
- [x] Tests unitarios para STT (mocked)
- [x] Tests unitarios para TTS (mocked)
- [x] Volume meter visual en UI

## US10 — Wake word (P2)

- [x] Implementar `voice/wake_word.py` (regex + cooldown + callbacks + singleton)
- [x] Wake word patterns: "Hey JARVIS", "Oye JARVIS", "Hey Jarv", "JARVIS"
- [x] Antibloqueo: cooldown 2s entre detecciones
- [x] Tests unitarios en `tests/unit/test_voice.py` (112 lines)
- [x] API `/api/voice/detect-wake`
- [x] Settings panel (selección de micrófono, sensibilidad wake word, velocidad TTS)

---

**Completado**: 17 tareas | **Pendiente**: 0 tareas
