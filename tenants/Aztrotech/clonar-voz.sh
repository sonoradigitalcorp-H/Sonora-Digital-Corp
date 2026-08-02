#!/bin/bash
# Clonar voz de César usando Kokoro TTS
# Usa el audio speech-cesar.ogg como referencia

set -e

AUDIO_REF="/home/mystic/sonora-digital-corp/state/media/speech-cesar.ogg"
OUT_DIR="/home/mystic/Escritorio/Aztrotech/voice-clone"

mkdir -p "$OUT_DIR"

echo "=== 1. Convertir audio de referencia a WAV 24kHz ==="
ffmpeg -y -i "$AUDIO_REF" -ar 24000 -ac 1 "$OUT_DIR/cesar-ref.wav"

echo "=== 2. Instalar Kokoro (si no está) ==="
pip install -q kokoro 2>/dev/null || true

echo "=== 3. Generar voz clonada ==="
python3 << 'PYEOF'
import os
import sys
import torch
import soundfile as sf
from pathlib import Path

AUDIO_REF = os.path.expanduser("~/sonora-digital-corp/state/media/speech-cesar.ogg")
OUT_DIR = os.path.expanduser("~/Escritorio/Aztrotech/voice-clone")

# Convert to WAV first
os.system(f"ffmpeg -y -i {AUDIO_REF} -ar 24000 -ac 1 {OUT_DIR}/cesar-ref.wav 2>/dev/null")

print("Cargando Kokoro...")
from kokoro import KPipeline

# Initialize with Spanish
pipeline = KPipeline(lang_code='es')

# Generate a sample with the voice reference
print("Generando voz clonada...")
generator = pipeline(
    "Hola, soy César Holguín de AstroTech. Este es un mensaje de prueba con mi voz clonada.",
    voice=str(Path(OUT_DIR) / "cesar-ref.wav"),
    speed=1.0,
)

for i, (gs, ps, audio) in enumerate(generator):
    sf.write(f"{OUT_DIR}/cesar-clonado-{i}.wav", audio, 24000)
    print(f"Fragmento {i} generado: {len(audio)/24000:.1f}s")

print("Voz clonada lista en voice-clone/")
PYEOF

echo "=== 4. Probar la voz clonada ==="
ls -la "$OUT_DIR/"
