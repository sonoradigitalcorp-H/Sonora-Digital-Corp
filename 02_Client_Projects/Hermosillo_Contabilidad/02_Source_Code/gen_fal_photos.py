#!/usr/bin/env python3
"""gen_fal_photos.py — Genera fotos del carrusel de la página de Nathaly con fal.ai.

CUANDO la FAL_KEY esté activa (regenerar en fal.ai/dashboard):
    python3 gen_fal_photos.py
Genera 5 imágenes del tema contadora/citas SAT y las sube al VPS.
"""

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

FAL_KEY = os.environ.get("FAL_KEY", "")
VPS_HTML = "/mnt/vps-data/html/hermosillo_assets/"  # destino en VPS (vía ssh)

# Tema: contadora en Hermosillo ayudando con citas del SAT, minimalista, profesional
PHOTOS = [
    {
        "id": "contadora_1",
        "prompt": (
            "Professional female accountant in Hermosillo, Mexico, at a clean modern desk, "
            "helping a smiling client with papers, warm natural light, minimal aesthetic, "
            "soft green and white tones, photorealistic, high detail, vertical 9:16"
        ),
    },
    {
        "id": "citas_sat",
        "prompt": (
            "Professional female accountant assisting a client booking an appointment on the "
            "SAT Mexico government portal, laptop screen with calendar, reassuring smile, "
            "modern bright office, minimal, photorealistic, vertical 9:16"
        ),
    },
    {
        "id": "declaracion",
        "prompt": (
            "Professional female accountant explaining a tax declaration to a small business "
            "owner, charts and documents on desk, calm professional atmosphere, Hermosillo "
            "Mexico, soft natural light, minimal white-green palette, photorealistic"
        ),
    },
    {
        "id": "importacion",
        "prompt": (
            "Professional female accountant with shipping documents and import manifests, "
            "modern logistics desk, globe and boxes subtle in background, Hermosillo Mexico, "
            "clean minimal, photorealistic, vertical 9:16"
        ),
    },
    {
        "id": "consultoria",
        "prompt": (
            "Professional female accountant consulting with a young entrepreneur over coffee, "
            "laptop showing growth charts, warm friendly, minimal modern office, Hermosillo, "
            "green-violet accents, photorealistic"
        ),
    },
]


def gen_image(prompt: str, out_path: Path) -> bool:
    body = json.dumps({
        "prompt": prompt,
        "image_size": {"width": 1024, "height": 1024},
        "num_images": 1,
        "num_inference_steps": 28,
        "guidance_scale": 3.5,
    }).encode()
    req = urllib.request.Request(
        "https://queue.fal.run/fal-ai/flux/dev",
        data=body,
        headers={"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            res = json.loads(resp.read())
        url = res.get("images", [{}])[0].get("url") or res.get("image", {}).get("url")
        if not url:
            print(f"  ✗ sin url: {json.dumps(res)[:200]}")
            return False
        urllib.request.urlretrieve(url, out_path)
        print(f"  ✓ {out_path.name} ({os.path.getsize(out_path)} bytes)")
        return True
    except urllib.error.HTTPError as e:
        print(f"  ✗ HTTP {e.code}: {e.read().decode()[:200]}")
        return False
    except Exception as e:
        print(f"  ✗ error: {e}")
        return False


def main():
    if not FAL_KEY or len(FAL_KEY) < 20:
        print("❌ FAL_KEY no válida. Regenera en https://fal.ai/dashboard y actualiza ~/.hermes/.env")
        sys.exit(1)
    out_dir = Path(__file__).resolve().parent / "photos"
    out_dir.mkdir(exist_ok=True)
    print("Generando fotos de contadora con fal.ai (flux/dev)...")
    ok = 0
    for photo in PHOTOS:
        path = out_dir / f"{photo['id']}.jpg"
        if gen_image(photo["prompt"], path):
            ok += 1
    print(f"\n{ok}/{len(PHOTOS)} fotos generadas en {out_dir}")
    print("Subir a VPS:")
    print(f"  scp {out_dir}/*.jpg ovh:{OUT_VPS}/")


if __name__ == "__main__":
    main()