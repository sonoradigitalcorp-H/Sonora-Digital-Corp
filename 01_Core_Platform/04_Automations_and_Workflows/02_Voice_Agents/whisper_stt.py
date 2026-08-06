#!/usr/bin/env python3
"""whisper_stt.py - Transcripción de audio a texto via CLI Whisper.
Conecta al CLI real de Whisper para pipeline audio→texto→memoria."""
import os, sys, subprocess, json

WHISPER_CLI = os.environ.get("WHISPER_CLI", "whisper")
MODEL = os.environ.get("WHISPER_MODEL", "base")
LANGUAGE = os.environ.get("WHISPER_LANGUAGE", "es")

def transcribe(audio_path, language=None):
    """Transcribe audio file to text using Whisper CLI."""
    language = language or LANGUAGE
    if not os.path.isfile(audio_path):
        return {"error": f"Archivo no encontrado: {audio_path}"}

    cmd = [WHISPER_CLI, audio_path, "--model", MODEL, "--language", language, "--output_format", "json"]
    output_dir = "/tmp/whisper_output"
    os.makedirs(output_dir, exist_ok=True)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=output_dir)
        if result.returncode != 0:
            return {"error": f"Whisper CLI failed: {result.stderr[:200]}"}

        output_file = os.path.join(output_dir, os.path.basename(audio_path).rsplit(".", 1)[0] + ".json")
        if os.path.isfile(output_file):
            with open(output_file) as f:
                data = json.load(f)
            text = data.get("text", "")
            segments = data.get("segments", [])
            return {"status": "success", "text": text, "segments": segments, "language": language}
        else:
            return {"error": "Whisper output file not found"}
    except subprocess.TimeoutExpired:
        return {"error": "Whisper transcription timed out"}
    except FileNotFoundError:
        return {"error": f"Whisper CLI not found: {WHISPER_CLI}. Install with: pip install openai-whisper"}
    except Exception as e:
        return {"error": str(e)}

def transcribe_and_route(audio_path, tenant="Aztrotech"):
    """Full pipeline: audio → text → OKF/Engram → answer."""
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Tools"))
    from okf_navigator import retrieve_context

    result = transcribe(audio_path)
    if "error" in result:
        return result

    text = result["text"]
    okf = retrieve_context(text, tenant)

    return {
        "transcription": text,
        "corpus": okf["corpus"],
        "context": okf["context"][:500] if okf["corpus"] != "none" else "No data found",
        "tenant": tenant
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Whisper STT for Sonora Digital Corp")
    parser.add_argument("audio", help="Path to audio file (mp3, wav, ogg, etc.)")
    parser.add_argument("--tenant", default="Aztrotech", help="Tenant name")
    parser.add_argument("--lang", default=None, help="Language override")
    args = parser.parse_args()

    print(f"Transcribiendo: {args.audio}")
    r = transcribe(args.audio, args.lang)
    if "error" in r:
        print(f"Error: {r['error']}")
        sys.exit(1)
    print(f"Texto: {r['text'][:200]}")
    print(f"Segments: {len(r.get('segments', []))}")

    print("\nEnrutando a OKF/Engram...")
    full = transcribe_and_route(args.audio, args.tenant)
    print(f"Corpus: {full['corpus']}")
    print(f"Contexto: {full['context'][:200]}")
