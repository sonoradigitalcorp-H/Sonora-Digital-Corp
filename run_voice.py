#!/usr/bin/env python3
"""
Mystic Voice Realtime — Runner.
Maneja imports desde directorio con guión.
"""
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))

# ─── Cargar módulos con importlib (porque voice-realtime tiene guión) ───
import importlib.util

_MODULES = {}

def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, str(REPO / path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _MODULES[name] = mod
    return mod

# Cargar en orden de dependencias
stt = _load_module("stt", "apps/voice-realtime/pipeline/stt.py")
tts = _load_module("tts", "apps/voice-realtime/pipeline/tts.py")
audio_mixer = _load_module("audio_mixer", "apps/voice-realtime/pipeline/audio_mixer.py")
intent_router = _load_module("intent_router", "apps/voice-realtime/intent_router.py")
voice_templates = _load_module("voice_templates", "apps/voice-realtime/voice_templates.py")
server = _load_module("server", "apps/voice-realtime/server.py")

# Reemplazar imports rotos en server.py
server.stt = stt
server.tts = tts
server.audio_mixer = audio_mixer
server.intent_router = intent_router
server.voice_templates = voice_templates

# Reasignar referencias del server a los módulos cargados
server.transcribe = stt.transcribe
server.VoiceActivityDetector = stt.VoiceActivityDetector
server.TTSEngine = tts.TTSEngine
server.AudioMixer = audio_mixer.AudioMixer
server.SOUNDSCAPES = audio_mixer.SOUNDSCAPES
server.IntentRouter = intent_router.IntentRouter
server.VoiceTemplateEngine = voice_templates.VoiceTemplateEngine

# Reconstruir instancias globales del server
server.tts_engine = tts.TTSEngine(provider="edge", voice="es-MX-DaliaNeural")
server.audio_mixer = audio_mixer.AudioMixer(soundscape="minimal")
server.intent_router = intent_router.IntentRouter(use_llm_fallback=True)
server.template_engine = voice_templates.VoiceTemplateEngine()
server.app.title = "Mystic Voice Realtime"

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("VOICE_PORT", "8900"))
    log_level = os.environ.get("VOICE_LOG", "info")
    print(f"🧿 Mystic Voice Realtime — corriendo en :{port}")
    uvicorn.run(server.app, host="127.0.0.1", port=port, log_level=log_level)
