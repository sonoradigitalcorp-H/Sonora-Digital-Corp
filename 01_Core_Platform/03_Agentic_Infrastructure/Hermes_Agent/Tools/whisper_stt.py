# Wrapper para Whisper CLI - Sonora Digital Corp
import subprocess
import sys

def transcribe_audio(audio_path, client_name):
    """
    Transcribe un archivo de audio usando Whisper CLI local.
    """
    print(f"[Hermes Tool] Transcribiendo audio para {client_name}...")
    try:
        # Ajusta el comando según tu instalación de Whisper
        result = subprocess.run(['whisper', audio_path, '--model', 'base', '--language', 'es'], 
                                capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f"Error en transcripción: {e}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(transcribe_audio(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "Unknown"))
