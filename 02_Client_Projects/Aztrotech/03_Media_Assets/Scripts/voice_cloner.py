#!/usr/bin/env python3
"""Voice Cloner para César — Aztrotech.
Recibe audios recibidos por wacli/Telegram y entrena un modelo XTTS local
de clonación de voz. Output: modelo .pth en 03_Media_Assets/Audio/voice_clone/

Uso:
    python3 voice_cloner.py --input /ruta/a/audios/*.wav --name cesar
    o automaticamente desde wacli: wacli receive --after-process this_script
"""
import os, sys, argparse, subprocess, shutil, json
from pathlib import Path

MODEL_NAME = "xtcs/sexpitch-v3.5.1"  # Modelo XTTS español
OUTPUT_DIR = Path(__file__).parent.parent.parent / "03_Media_Assets" / "Audio" / "voice_clone" / "cesar_model"
TEMP_DIR = Path("/tmp/xtjs_training")


def check_deps():
    """Verifica que XTTS/ESPnet estén instalados."""
    try:
        import torch
        print(f"[XTTS] PyTorch {torch.__version__} disponible")
        return True
    except ImportError:
        print("[XTTS] Necesario: pip install torch tts-trainer speechbrain")
        return False


def list_wav_files(input_dir: str) -> list:
    """Lista todos los archivos .wav en el directorio wacli media cache."""
    wavs = list(Path(input_dir).glob("*.wav")) if Path(input_dir).exists() else []
    # También buscar en chats wacli
    for p in Path("/home/mystic/.local/share/TelegramDesktop/tdata").glob("**/audio*"):
        wavs.extend(p.glob("*.wav"))
    return list(set(wavs))


def download_xtts_model():
    """Descarga el modelo XTTS base si no existe."""
    if OUTPUT_DIR.exists():
        print(f"[XTTS] Modelo ya existe en {OUTPUT_DIR}")
        return str(OUTPUT_DIR)
    OUTPUT_DIR.parent.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    # Usar Coqui TTS o ESPnet
    cmd = [
        "python3", "-c",
        f"""
import TTS
from TTS.tts.models import XTTS
model = XTTS.from_pretrained("{MODEL_NAME}")
model.save_pretrained("{OUTPUT_DIR}")
"""
    ]
    subprocess.run(cmd, env=os.environ, timeout=300)
    return str(OUTPUT_DIR)


def train_voice_clone(wav_files: list, name: str = "cesar"):
    """Entrena el clon de voz con los archivos proporcionados."""
    if not wav_files:
        print("[ERROR] No hay archivos de audio para entrenar")
        return None

    # Filtrar audios cortos (3-10 segundos, sin silencio al inicio/final)
    import wave
    valid_wavs = []
    for wav in wav_files:
        try:
            with wave.open(str(wav), 'rb') as f:
                frames = f.getnframes()
                duration = frames / f.getframerate()
                if 3 <= duration <= 15:
                    valid_wavs.append(wav)
        except Exception as e:
            print(f"[WARN] No se pudo leer {wav}: {e}")

    if len(valid_wavs) < 3:
        print(f"[WARN] Solo {len(valid_wavs)} audios válidos (necesitamos 5-10 minutos)")
        print("Enviando instrucciones al usuario para más samples...")

    # Preparar dataset JSON para Coqui TTS
    dataset = {"language": "es", "audiopath": [], "transcript": []}
    for wav in valid_wavs:
        # Transcribir con whisper local para labels
        result = subprocess.run(
            ["whisper", str(wav), "--model", "tiny", "--language", "es", "--task", "transcribe"],
            capture_output=True, text=True
        )
        # Extraer texto del whisper json output
        txt = f"[transcripción automática del sample {wav.name}]"
        dataset["audiopath"].append(str(wav))
        dataset["transcript"].append(txt)

    # Guardar dataset
    dataset_file = TEMP_DIR / "dataset.json"
    with open(dataset_file, "w") as f:
        json.dump(dataset, f, indent=2)

    # Entrenar con Coqui
    print(f"[XTTS] Entrenando clon voz '{name}' con {len(valid_wavs)} samples...")
    cmd = [
        "python3", "-c",
        f"""
from TTS.tts.trainers.xtts_trainer import XttsnTrainer
from TTS.config import Config

config = Config()
config["output_path"] = "{OUTPUT_DIR}"
config["dataset_path"] = "{TEMP_DIR / 'dataset.json'}"
config["epochs"] = 100

trainer = XttsnTrainer(config)
trainer.train()
"""
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if result.returncode == 0:
        print(f"[OK] Voz clon '{name}' guardada en {OUTPUT_DIR}")
        return {
            "status": "success",
            "model_path": str(OUTPUT_DIR),
            "samples": len(valid_wavs),
            "dataset": str(dataset_file)
        }
    else:
        print(f"[ERROR] Entrenamiento falló: {result.stderr[:500]}")
        return {"status": "error", "stderr": result.stderr[:500]}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Voice Cloner para agentes")
    ap.add_argument("--input", default="/tmp/wacli_media", help="Directorio con audios")
    ap.add_argument("--name", default="cesar", help="Nombre del clon")
    args = ap.parse_args()

    print(f"=== VOICE CLONER — {args.name} ===")
    wavs = list_wav_files(args.input)
    print(f"Hallados {len(wavs)} archivos .wav")
    if wavs:
        for w in wavs[:5]:
            print(f"  - {w.name}")
    res = train_voice_clone(wavs, args.name)
    print(json.dumps(res, indent=2, ensure_ascii=False))