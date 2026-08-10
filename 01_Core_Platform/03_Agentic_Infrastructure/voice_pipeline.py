#!/usr/bin/env python3
"""voice_pipeline.py — Wrapper unificado de voz: STT + TTS + envío.

Reusa voice_reply.py y whisper_stt.py. Determinista salvo modelos.
"""

import os
import sys
import tempfile
from pathlib import Path

BASE = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE / "01_Core_Platform" / "04_Automations_and_Workflows" / "02_Voice_Agents"))
sys.path.insert(0, str(BASE / "01_Core_Platform" / "03_Agentic_Infrastructure"))

# Importar funciones existentes
try:
    from voice_reply import text_to_ogg, send_telegram_voice, _token, BOTS, DEFAULT_VOICE, FFMPEG
except ImportError:
    # Fallback si no está disponible
    text_to_ogg = None
    send_telegram_voice = None
    _token = None
    BOTS = {}
    DEFAULT_VOICE = {}
    FFMPEG = None


def stt_audio(audio_path: str, model: str = "small", language: str = "es") -> str:
    """
    Speech-to-Text usando faster-whisper local (CPU, int8).
    Retorna texto transcrito.
    """
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return "[ERROR: faster-whisper no instalado]"

    try:
        model_instance = WhisperModel(model, device="cpu", compute_type="int8")
        segments, info = model_instance.transcribe(audio_path, language=language, beam_size=5)
        text = " ".join(seg.text for seg in segments).strip()
        return text
    except Exception as e:
        return f"[ERROR STT: {e}]"


def tts_text(text: str, voice: str = "es-MX-DaliaNeural", out_path: str = None) -> str:
    """
    Text-to-Speech usando edge-tts + ffmpeg → OGG.
    Retorna ruta del archivo OGG.
    """
    if text_to_ogg is None:
        return "[ERROR: voice_reply no disponible]"

    if out_path is None:
        out_path = tempfile.mktemp(suffix=".ogg")

    try:
        return text_to_ogg(text, voice, Path(out_path))
    except Exception as e:
        return f"[ERROR TTS: {e}]"


def send_voice_message(bot: str, chat_id: str, text: str, voice: str = None) -> bool:
    """
    Pipeline completo: TTS → OGG → sendTelegramVoice.
    Retorna True si éxito.
    """
    if send_telegram_voice is None:
        print("[ERROR] voice_reply no disponible")
        return False

    voice = voice or DEFAULT_VOICE.get(bot, "es-MX-DaliaNeural")
    out_path = tempfile.mktemp(suffix=".ogg")

    try:
        ogg_path = text_to_ogg(text, voice, Path(out_path))
        return send_telegram_voice(bot, chat_id, ogg_path)
    except Exception as e:
        print(f"[ERROR] send_voice_message: {e}")
        return False


def process_voice_message(
    bot: str,
    chat_id: str,
    audio_path: str,
    onboarding_engine=None,
    lead_classifier=None,
    tenant: str = "aztrotech"
) -> dict:
    """
    Pipeline completo de mensaje de voz:
    1. STT (audio → texto)
    2. Clasificar intención (lead_classifier)
    3. Ejecutar acción (onboarding_engine)
    4. Generar respuesta (texto + opcional voz)
    5. Enviar respuesta
    Retorna dict con resultado completo.
    """
    result = {
        "stt_text": "",
        "classification": None,
        "action_taken": None,
        "response_text": "",
        "response_voice_path": None,
        "sent": False,
        "error": None
    }

    # 1. STT
    stt_text = stt_audio(audio_path)
    if stt_text.startswith("[ERROR"):
        result["error"] = stt_text
        return result
    result["stt_text"] = stt_text

    # 2. Clasificar
    if lead_classifier is None:
        from lead_classifier import classify_lead_intent
        lead_classifier = classify_lead_intent

    classification = lead_classifier(tenant, stt_text)
    result["classification"] = classification.model_dump()

    # 3. Ejecutar acción según clasificación
    if onboarding_engine is None:
        from onboarding_engine import OnboardingEngine
        # Usar DB por defecto
        db_path = Path.home() / ".openclaw" / "workspace" / "leads_aztrotech.db"
        onboarding_engine = OnboardingEngine(str(db_path), tenant)

    action = classification.accion_requerida
    intent = classification.intencion
    campos = classification.campos

    try:
        if action == "capture" or intent == "nuevo_lead":
            # Capturar lead
            lead_id = onboarding_engine.capture_lead(tenant, chat_id, campos)
            result["action_taken"] = f"capture:{lead_id}"
            result["response_text"] = classification.respuesta_sugerida

        elif action == "schedule" or intent == "agendar_cita":
            # Necesita lead_id existente o crear uno
            lead_id = campos.get("lead_id")
            if not lead_id:
                # Buscar lead reciente de este chat
                leads = onboarding_engine.list_leads(tenant=tenant, limit=1)
                if leads:
                    lead_id = leads[0]["id"]
                else:
                    lead_id = onboarding_engine.capture_lead(tenant, chat_id, campos)

            fecha = campos.get("fecha")
            hora = campos.get("hora")
            if fecha and hora:
                schedule_result = onboarding_engine.schedule_cita(lead_id, fecha, hora)
                result["action_taken"] = f"schedule:{schedule_result}"
                if schedule_result["success"]:
                    result["response_text"] = f"Perfecto, cita agendada para el {fecha} a las {hora}. Te confirmaré por este medio."
                    # Notificar a César
                    notify_result = onboarding_engine.notify_cesar(lead_id)
                    result["action_taken"] += f" + notify:{notify_result}"
                else:
                    result["response_text"] = f"Esa fecha/hora no está disponible: {schedule_result['error']}. ¿Otra opción?"
            else:
                result["response_text"] = "Necesito fecha y hora para agendar. ¿Qué día y a qué hora te viene bien?"

        elif action == "escalar" or intent in ["tecnico_dificil", "escalar_cesar"]:
            # Escalar a César
            lead_id = campos.get("lead_id")
            if not lead_id:
                leads = onboarding_engine.list_leads(tenant=tenant, limit=1)
                lead_id = leads[0]["id"] if leads else onboarding_engine.capture_lead(tenant, chat_id, {"nombre": "Lead voz", "empresa": "", "servicio": "consulta"})

            notify_result = onboarding_engine.notify_cesar(lead_id)
            result["action_taken"] = f"escalar:{notify_result}"
            result["response_text"] = classification.respuesta_sugerida or "Eso es técnico, te paso con César directamente."

        elif action == "responder" or intent in ["precio", "info_general", "saludo"]:
            # Responder con OKF si es precio
            result["action_taken"] = "responder"
            result["response_text"] = classification.respuesta_sugerida

        else:
            result["action_taken"] = "none"
            result["response_text"] = "Entendido. ¿En qué más te ayudo?"

    except Exception as e:
        result["error"] = f"Error en acción: {e}"
        result["response_text"] = "Hubo un problema procesando tu solicitud. Intenta de nuevo."

    # 4. Generar y enviar respuesta en voz si el usuario usó voz
    if result["response_text"]:
        voice = DEFAULT_VOICE.get(bot, "es-MX-DaliaNeural")
        ogg_path = tempfile.mktemp(suffix=".ogg")
        tts_result = tts_text(result["response_text"], voice, ogg_path)

        if not tts_result.startswith("[ERROR"):
            result["response_voice_path"] = tts_result
            # Enviar
            sent = send_telegram_voice(bot, chat_id, tts_result)
            result["sent"] = sent
        else:
            result["error"] = tts_result

    return result


def main():
    """CLI para testing."""
    import argparse
    ap = argparse.ArgumentParser(description="Voice Pipeline CLI")
    sub = ap.add_subparsers(dest="cmd")

    p_stt = sub.add_parser("stt", help="Solo STT")
    p_stt.add_argument("audio", help="Ruta audio")

    p_tts = sub.add_parser("tts", help="Solo TTS")
    p_tts.add_argument("text", help="Texto a sintetizar")
    p_tts.add_argument("--voice", default="es-MX-DaliaNeural")
    p_tts.add_argument("--out", default="/tmp/test_voice.ogg")

    p_send = sub.add_parser("send", help="Enviar voz a Telegram")
    p_send.add_argument("--bot", required=True, choices=list(BOTS.keys()) if BOTS else ["aztroc", "rye"])
    p_send.add_argument("--chat", required=True)
    p_send.add_argument("--text", required=True)
    p_send.add_argument("--voice", default="es-MX-DaliaNeural")

    p_full = sub.add_parser("process", help="Pipeline completo voz")
    p_full.add_argument("--bot", required=True)
    p_full.add_argument("--chat", required=True)
    p_full.add_argument("--audio", required=True)
    p_full.add_argument("--tenant", default="aztrotech")

    args = ap.parse_args()

    if args.cmd == "stt":
        print(stt_audio(args.audio))
    elif args.cmd == "tts":
        print(tts_text(args.text, args.voice, args.out))
    elif args.cmd == "send":
        ok = send_voice_message(args.bot, args.chat, args.text, args.voice)
        print("OK" if ok else "FAIL")
    elif args.cmd == "process":
        result = process_voice_message(args.bot, args.chat, args.audio, tenant=args.tenant)
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        ap.print_help()


if __name__ == "__main__":
    main()