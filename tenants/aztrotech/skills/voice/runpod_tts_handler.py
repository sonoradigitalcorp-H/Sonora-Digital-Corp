"""
RunPod TTS Handler — Se ejecuta dentro del worker serverless de RunPod.

Recibe: {"input": {"text": "...", "voice": "cesar", "language": "Spanish"}}
Retorna: {"output": {"audio": "<base64 wav>", "cost": 0.001}}

Deploy:
  1. Construir imagen: docker build -f Dockerfile.runpod -t qwen3-tts-runpod .
  2. Push a Docker Hub / GHCR
  3. Crear endpoint serverless en RunPod con la imagen
  4. Configurar RUNPOD_API_KEY y RUNPOD_TTS_ENDPOINT
"""

import base64
import json
import os
import tempfile
import time
from pathlib import Path

# ========== MODELO ==========
_model = None
_ref_audio = None
_ref_text = None


def load_model():
    global _model, _ref_audio, _ref_text
    if _model is not None:
        return

    import torch
    from qwen_tts import Qwen3TTSModel

    # Cargar modelo en GPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Cargando Qwen3-TTS en {device}...")

    _model = Qwen3TTSModel.from_pretrained(
        "Qwen/Qwen3-TTS-12Hz-0.6B-Base",
        device_map=device,
        dtype=torch.float16 if device == "cuda" else torch.float32,
    )
    _model.eval()

    # Cargar referencia de voz
    ref_audio_path = os.environ.get(
        "CESAR_REF_AUDIO", "/app/cesar-ref-short.wav"
    )
    ref_text_path = os.environ.get(
        "CESAR_REF_TEXT", "/app/ref_text_short.txt"
    )

    if os.path.exists(ref_text_path):
        with open(ref_text_path) as f:
            _ref_text = f.read().strip()
    
    if os.path.exists(ref_audio_path):
        _ref_audio = ref_audio_path

    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    logger.info(f"Modelo listo en {device}. Voz de referencia: {os.path.basename(ref_audio_path)}")


def synthesize(text: str, voice: str = "cesar", language: str = "Spanish") -> dict:
    """Sintetiza texto a audio con clonación de voz."""
    import soundfile as sf

    load_model()
    start = time.time()

    # Voice cloning con referencia de César
    wavs, sr = _model.generate_voice_clone(
        text=text,
        language=language,
        ref_audio=_ref_audio,
        ref_text=_ref_text,
    )

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        tmp_path = f.name
    sf.write(tmp_path, wavs[0], sr)

    with open(tmp_path, "rb") as f:
        audio_b64 = base64.b64encode(f.read()).decode()

    os.unlink(tmp_path)

    latency = (time.time() - start) * 1000
    # Costo estimado: RTX 4090 ~$0.49/hr, cada TTS ~1s → ~$0.00014
    cost = round(0.49 / 3600 * (latency / 1000), 6)

    return {
        "audio": audio_b64,
        "sample_rate": sr,
        "latency_ms": round(latency, 1),
        "cost": cost,
    }


# ========== INTERFAZ RUNPOD ==========
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger("runpod-tts")

try:
    import runpod

    def handler(job):
        """Handler RunPod serverless."""
        job_input = job.get("input", {})
        text = job_input.get("text", "")
        voice = job_input.get("voice", "cesar")
        language = job_input.get("language", "Spanish")

        logger.info(f"TTS: '{text[:50]}...' (voice={voice})")
        result = synthesize(text, voice, language)
        logger.info(f"TTS OK: {result['latency_ms']}ms, ${result['cost']}")

        return {"output": result}

    # Iniciar worker RunPod
    runpod.serverless.start({"handler": handler})

except ImportError:
    logger.info("runpod SDK no instalado. Usar modo directo: python3 runpod_tts_handler.py --text '...'")

    if __name__ == "__main__":
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--text", required=True, help="Texto a sintetizar")
        parser.add_argument("--voice", default="cesar")
        parser.add_argument("--language", default="Spanish")
        args = parser.parse_args()

        result = synthesize(args.text, args.voice, args.language)
        print(json.dumps(result, ensure_ascii=False, indent=2))
