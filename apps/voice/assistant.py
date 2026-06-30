"""
JARVIS Voice Assistant — Full pipeline
Wake word → STT → response → TTS
Run: python3 voice/assistant.py
"""

import logging
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s %(message)s")
log = logging.getLogger("jarvis.assistant")

from voice import WakeWordDetector, list_microphones
from voice.tts import get_engine


def process_command(text: str) -> str:
    """Process voice command and return response."""
    text_lower = text.lower().strip()
    
    if not text_lower:
        return "No te escuche bien. Repite por favor."
    
    if "hora" in text_lower:
        return f"Son las {time.strftime('%I:%M %p')}"
    
    if "quien eres" in text_lower or "who are you" in text_lower:
        return "Soy JARVIS, tu asistente personal de Sonora Digital Corp."
    
    # Default: try LLM
    try:
        from src.core.llm import query_llm
        response = query_llm(text, system="Eres JARVIS, asistente de Sonora Digital Corp. Responde en español, breve y util.")
        return response[:500] if response else "No pude procesar eso ahora."
    except Exception as e:
        log.warning(f"LLM unavailable: {e}")
        return f"Recibi tu mensaje: {text}. Pero el modulo de IA no esta disponible en este momento."


def interactive_mode():
    """Interactive text-based mode (for testing)."""
    print("\n" + "="*50)
    print("JARVIS Voice Assistant — Interactive Mode")
    print("Type 'voice' for voice input, 'quit' to exit")
    print("="*50)
    
    engine = get_engine()
    engine.start()
    
    while True:
        try:
            cmd = input("\nYou: ").strip()
            if cmd.lower() in ("quit", "exit", "q"):
                engine.say("Hasta luego!")
                time.sleep(1)
                break
            
            if cmd.lower() == "voice":
                print("Escuchando... (habla ahora)")
                list_microphones()
                continue
            
            if cmd:
                response = process_command(cmd)
                print(f"JARVIS: {response}")
                engine.say(response)
        
        except (EOFError, KeyboardInterrupt):
            break
    
    engine.stop()
    print("\nJARVIS offline.")


def voice_loop():
    """Full voice mode: wake word → listen → respond."""
    print("\n" + "="*50)
    print("JARVIS Voice Loop — Say 'Hey JARVIS' to start")
    print("Press Ctrl+C to exit")
    print("="*50)
    
    detector = WakeWordDetector()
    engine = get_engine()
    engine.start()
    
    def on_wake():
        print("\n🔊 JARVIS activado!")
        engine.say("Dime", priority=True)
        time.sleep(1)
        # After wake word, listen for command
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            with sr.Microphone() as source:
                print("🎤 Escuchando...")
                r.adjust_for_ambient_noise(source, duration=0.3)
                audio = r.listen(source, timeout=5, phrase_time_limit=10)
            print("Procesando...")
            text = r.recognize_google(audio, language="es-MX")
            print(f"Tu: {text}")
            
            response = process_command(text)
            print(f"JARVIS: {response}")
            engine.say(response)
        except sr.WaitTimeoutError:
            print("No te escuche")
            engine.say("No te escuche, intenta de nuevo")
        except sr.UnknownValueError:
            print("No entendi")
            engine.say("No entendi lo que dijiste")
        except Exception as e:
            print(f"Error: {e}")
    
    detector.on_wake(on_wake)
    print("\nEsperando 'Hey JARVIS'...")
    
    try:
        detector.start_background_listening()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDeteniendo...")
    finally:
        detector.stop()
        engine.stop()
    print("\nJARVIS offline.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "voice":
        voice_loop()
    else:
        interactive_mode()
