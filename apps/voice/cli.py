"""
JARVIS Voice CLI — Testing and debugging tool.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice import (
    WakeWordDetector,
    list_microphones,
    play_audio,
    speak,
    transcribe,
)


def cmd_mic():
    """List available microphones."""
    print("Microphones disponibles:")
    list_microphones()


def cmd_transcribe(path):
    """Transcribe an audio file."""
    if not os.path.exists(path):
        print(f"Error: File not found: {path}")
        return
    print(f"Transcribiendo: {path}...")
    text = transcribe(path)
    print(f"Texto: {text}")


def cmd_speak(text):
    """Convert text to speech."""
    print(f"Generando voz para: {text}")
    path = speak(text)
    if path:
        print(f"Audio generado: {path}")
        play_audio(path)
    else:
        print("Error: No se pudo generar audio")


def cmd_wake():
    """Test wake word detection."""
    detector = WakeWordDetector()

    def on_wake():
        print("🔊 Wake word detected!")

    detector.on_wake(on_wake)

    print("Wake word detector ready. Type phrases to test:")
    print("  (type 'Hey JARVIS' or 'Oye JARVIS')")
    print("  (type 'quit' to exit)\n")

    while True:
        try:
            line = input("> ").strip()
            if line.lower() in ("quit", "exit", "q"):
                break
            if detector.detect(line):
                print("  ✅ Detected!")
            else:
                print("  ❌ Not detected")
        except (EOFError, KeyboardInterrupt):
            break

    print("Wake word test complete")


def cmd_listen():
    """Start background listening mode."""
    detector = WakeWordDetector()

    def on_wake():
        print("\n🔊 Wake word detected! Listening...")

    detector.on_wake(on_wake)
    print("Starting background listening (Ctrl+C to stop)...")
    print("Say 'Hey JARVIS' to trigger")

    try:
        detector.start_background_listening()
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        detector.stop()


def help_text():
    print("""
JARVIS Voice CLI

Usage:
  python -m voice.cli mic              List microphones
  python -m voice.cli transcribe <file> Transcribe audio file
  python -m voice.cli speak <text>     Text-to-speech
  python -m voice.cli wake             Test wake word detection
  python -m voice.cli listen           Background wake word listening
""")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        help_text()
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "mic":
        cmd_mic()
    elif cmd == "transcribe" and len(sys.argv) > 2:
        cmd_transcribe(sys.argv[2])
    elif cmd == "speak" and len(sys.argv) > 2:
        cmd_speak(" ".join(sys.argv[2:]))
    elif cmd == "wake":
        cmd_wake()
    elif cmd == "listen":
        cmd_listen()
    else:
        help_text()
