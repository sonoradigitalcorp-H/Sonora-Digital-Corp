#!/usr/bin/env python3
"""WhatsApp Voice Pipeline - Sonora Digital Corp.
Flujo completo: audio WhatsApp → transcripción → procesamiento → respuesta de voz → WhatsApp."""
import os, sys, json, tempfile, subprocess, asyncio

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Hermes_Agent", "Tools")
sys.path.insert(0, TOOLS_DIR)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "05_Shared_Libraries", "SDK_Python"))

from sdc_sdk import SDC_Client
from okf_navigator import retrieve_context

WACLI = os.environ.get("WACLI", "wacli")
WHISPER = os.environ.get("WHISPER_CLI", "whisper")
EDGE_TTS = os.environ.get("EDGE_TTS", "edge-tts")
WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "base")
WHISPER_LANGUAGE = os.environ.get("WHISPER_LANGUAGE", "es")
TTS_VOICE = os.environ.get("TTS_VOICE", "es-MX-JorgeNeural")
DEFAULT_TENANT = os.environ.get("DEFAULT_TENANT", "Aztrotech")

def receive_audio_from_whatsapp():
    """Receive audio message from WhatsApp via wacli."""
    try:
        result = subprocess.run(
            [WACLI, "receive", "--format", "json"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
        return None
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        return None

def transcribe_audio(audio_path):
    """Transcribe audio file using Whisper CLI."""
    if not os.path.isfile(audio_path):
        return {"error": f"Audio file not found: {audio_path}"}

    output_dir = tempfile.mkdtemp()
    try:
        result = subprocess.run(
            [WHISPER, audio_path, "--model", WHISPER_MODEL, "--language", WHISPER_LANGUAGE,
             "--output_format", "json", "--output_dir", output_dir],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0:
            return {"error": f"Whisper failed: {result.stderr[:200]}"}

        base_name = os.path.basename(audio_path).rsplit(".", 1)[0]
        json_path = os.path.join(output_dir, f"{base_name}.json")
        if os.path.isfile(json_path):
            with open(json_path) as f:
                data = json.load(f)
            return {"status": "success", "text": data.get("text", ""), "segments": data.get("segments", [])}
        return {"error": "Whisper output not found"}
    except subprocess.TimeoutExpired:
        return {"error": "Whisper transcription timed out"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        import shutil
        shutil.rmtree(output_dir, ignore_errors=True)

def process_with_hermes(text, tenant=DEFAULT_TENANT):
    """Process text with OKF + Engram + OpenRouter."""
    client = SDC_Client(tenant)

    okf = retrieve_context(text, tenant)
    okf_context = ""
    if okf["corpus"] == "okf":
        okf_context = f"[OKF - {okf['concept_id']}]\n{okf['context'][:600]}"
    elif okf["corpus"] == "rag":
        okf_context = f"[Engram - experiencial]\n{okf['context'][:600]}"

    messages = [
        {"role": "system", "content": "Eres Hermes de Sonora Digital Corp. Responde en español, conciso. Cita la fuente."},
        {"role": "user", "content": f"Pregunta: {text}\n\nContexto:\n{okf_context if okf_context else 'Sin datos en ninguna capa.'}\n\nResponde de forma natural."}
    ]

    result = client.call_llm(messages)
    if result.get("status") == "success":
        return result["content"].strip()
    return "no tengo datos verificados"

def text_to_speech(text, output_path):
    """Convert text to speech using edge-tts."""
    try:
        result = subprocess.run(
            [EDGE_TTS, "--voice", TTS_VOICE, "--text", text, "--write-media", output_path],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0 and os.path.isfile(output_path):
            return {"status": "success", "path": output_path}
        return {"error": f"edge-tts failed: {result.stderr[:200]}"}
    except subprocess.TimeoutExpired:
        return {"error": "TTS timed out"}
    except Exception as e:
        return {"error": str(e)}

def send_audio_to_whatsapp(audio_path, recipient=None):
    """Send audio message back to WhatsApp via wacli."""
    if not os.path.isfile(audio_path):
        return {"error": f"Audio file not found: {audio_path}"}

    try:
        result = subprocess.run(
            [WACLI, "send", "--audio", audio_path, "--to", recipient or DEFAULT_TENANT],
            capture_output=True, text=True, timeout=30
        )
        return {"status": "success" if result.returncode == 0 else "failed", "returncode": result.returncode}
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return {"error": str(e)}

def save_memory_if_needed(text, tenant=DEFAULT_TENANT):
    """Save important interactions to memory."""
    sys.path.insert(0, TOOLS_DIR)
    from engram_memory import save_memory
    try:
        return save_memory(text, tenant)
    except Exception:
        return None

async def run_pipeline():
    """Main pipeline: WhatsApp audio → transcription → processing → TTS → WhatsApp response."""
    print("=" * 60)
    print("WHATSAPP VOICE PIPELINE - Sonora Digital Corp")
    print("=" * 60)

    # Step 1: Receive audio from WhatsApp
    print("\n[1/5] Recibiendo audio de WhatsApp...")
    audio_msg = receive_audio_from_whatsapp()
    if not audio_msg:
        print("⚠️ No audio message received")
        return

    audio_path = audio_msg.get("media_path") or audio_msg.get("audio_path")
    if not audio_path:
        print("⚠️ No audio path in message")
        return
    print(f"✅ Audio recibido: {audio_path}")

    # Step 2: Transcribe with Whisper
    print("\n[2/5] Transcribiendo con Whisper...")
    transcript = transcribe_audio(audio_path)
    if "error" in transcript:
        print(f"❌ Transcription error: {transcript['error']}")
        return
    text = transcript["text"]
    print(f"✅ Texto: {text[:200]}")

    # Step 3: Process with Hermes + OKF
    print("\n[3/5] Procesando con Hermes + OKF...")
    tenant = audio_msg.get("tenant", DEFAULT_TENANT)
    answer = process_with_hermes(text, tenant)
    print(f"✅ Respuesta: {answer[:200]}")

    # Step 4: Convert to speech with edge-tts
    print("\n[4/5] Generando audio de respuesta...")
    output_dir = tempfile.mkdtemp()
    audio_output = os.path.join(output_dir, "response.mp3")
    tts_result = text_to_speech(answer, audio_output)
    if "error" in tts_result:
        print(f"❌ TTS error: {tts_result['error']}")
        return
    print(f"✅ Audio generado: {audio_output}")

    # Step 5: Send audio back to WhatsApp
    print("\n[5/5] Enviando audio de vuelta a WhatsApp...")
    send_result = send_audio_to_whatsapp(audio_output, tenant)
    if "error" in send_result:
        print(f"❌ Send error: {send_result['error']}")
    else:
        print(f"✅ Audio enviado a WhatsApp (tenant: {tenant})")

    # Save to memory
    print("\n[Memoria] Guardando interacción...")
    save_memory_if_needed(f"User: {text} | Answer: {answer}", tenant)

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETO: WhatsApp → Audio → Texto → Cerebro → Voz → WhatsApp")
    print("=" * 60)

    # Cleanup
    import shutil
    shutil.rmtree(output_dir, ignore_errors=True)

if __name__ == "__main__":
    asyncio.run(run_pipeline())
