#!/usr/bin/env python3
"""gen_fal_images.py — Genera FOTOS reales con FAL AI (fal-ai/flux-dev) para el carrusel
de la landing Hermosillo. Fondo blanco minimalista, temática contabilidad, SIN personas.

Uso: python3 gen_fal_images.py [--out DIR] [--model MODEL]
"""
import os
import sys
import time
from pathlib import Path

import fal_client

BASE = Path(__file__).resolve().parent
OUT = Path(sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else BASE / ".." / "03_Media_Assets" / "canva")
MODEL = sys.argv[sys.argv.index("--model") + 1] if "--model" in sys.argv else "fal-ai/flux/dev"

# Ratio del carrusel: aspect-[3.4/1] → 1344x384 = 3.5:1 (múltiplos de 32, sin recorte brusco)
W, H = 1344, 384

STYLE = (
    "ultra realistic professional photograph, clean minimalist white background, "
    "soft studio lighting, high key, subtle shadows, product photography style, "
    "sharp focus, high detail, 4k, no people, no faces, no text, no watermark"
)

SCENES = {
    "contabilidad": (
        "A tidy accountant desk scene: neatly stacked financial documents and ledgers, "
        "a silver calculator, a black pen, a small potted succulent. " + STYLE
    ),
    "citas_sat": (
        "A clean minimalist desk with an open planner calendar showing a circled appointment, "
        "a pen resting beside it, soft neutral tones. " + STYLE
    ),
    "declaracion": (
        "Tax declaration paperwork on a white desk: official forms neatly arranged, a stamp, "
        "a calculator at the corner, clean composition. " + STYLE
    ),
    "importacion": (
        "A tidy scene with a customs cargo manifest document, a small shipping box, "
        "and a clipboard, minimalist white desk. " + STYLE
    ),
    "dashboard": (
        "A modern laptop on a white desk displaying a clean financial dashboard with charts "
        "and graphs, minimalist office scene, subtle green accents. " + STYLE
    ),
}


def gen(name: str, prompt: str) -> str:
    """Genera una imagen vía fal_client.subscribe y la guarda. Devuelve la ruta local."""
    result = fal_client.subscribe(
        MODEL,
        arguments={
            "prompt": prompt,
            "image_size": {"width": W, "height": H},
            "num_images": 1,
            "num_inference_steps": 28,
            "guidance_scale": 3.5,
        },
    )
    url = result["images"][0]["url"]
    out_path = OUT / f"{name}.jpg"

    import urllib.request

    urllib.request.urlretrieve(url, out_path)
    size = out_path.stat().st_size
    print(f"✓ {name}.jpg ({size//1024}KB)")
    return str(out_path)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, prompt in SCENES.items():
        for attempt in range(2):
            try:
                gen(name, prompt)
                break
            except Exception as e:
                print(f"✗ {name} intento {attempt+1}: {e}")
                if attempt == 0:
                    time.sleep(5)
    print(f"Listo en {OUT}")


if __name__ == "__main__":
    main()