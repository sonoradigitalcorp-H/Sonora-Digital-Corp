#!/usr/bin/env python3
"""gen_reel_hermosillo.py — Reel vertical 1080x1920 con marca, cortes 4-6s (dopamina).

Usa fotos FAL + ffmpeg (zoompan + overlay). Los textos se generan con Pillow como
PNG (ffmpeg static no trae drawtext). Salida lista para redes.
Uso: python3 gen_reel_hermosillo.py
"""

import os
import subprocess
import tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parent
PHOTOS = BASE / ".." / "03_Media_Assets" / "photos"
OUT = PHOTOS / "reel_hermosillo.mp4"
W, H = 1080, 1920

SEGS = [
    ("contadora_1.jpg", "Contabilidad en orden"),
    ("citas_sat.jpg", "Citas SAT gestionadas"),
    ("declaracion.jpg", "Declaraciones sin errores"),
    ("vision_celular_asistente.jpg", "Asistente IA 24/7"),
    ("vision_dashboard.jpg", "Dashboard en tiempo real"),
]


def make_text_png(text: str, path: Path, size: int = 72):
    """PNG transparente con texto centrado inferior."""
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except Exception:
        font = ImageFont.load_default()
    # caja de fondo semi
    d.rectangle([0, H - 340, W, H], fill=(0, 0, 0, 150))
    # texto centrado
    bbox = d.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((W - tw) / 2, H - 300 - th / 2), text, font=font, fill=(255, 255, 255, 255))
    img.save(path)


def main():
    tmp = Path(tempfile.mkdtemp(prefix="reel_"))
    segs = []
    for i, (imgname, txt) in enumerate(SEGS):
        img = PHOTOS / imgname
        if not img.exists():
            continue
        png = tmp / f"t{i}.png"
        make_text_png(txt, png)
        seg = tmp / f"s{i}.mp4"
        # zoompan + overlay texto
        cmd = [
            "ffmpeg", "-y", "-loop", "1", "-i", str(img), "-i", str(png),
            "-t", "5", "-r", "30",
            "-filter_complex",
            f"[0:v]scale=2160:3840:force_original_aspect_ratio=increase,"
            f"crop=2160:3840,zoompan=z='1+0.08*on/150':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H},format=yuv420p[v];"
            f"[1:v]format=rgba[t];[v][t]overlay=0:0:shortest=1[out]",
            "-map", "[out]", "-c:v", "libx264", "-preset", "medium", "-crf", "23", str(seg),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"✗ {imgname}: {r.stderr[-300:]}")
            continue
        segs.append(str(seg))
        print(f"✓ {imgname}")

    if not segs:
        print("Sin segmentos generados")
        return 1

    # Concat + marca en esquina (PNG marca)
    brand = tmp / "brand.png"
    make_text_png("Nathaly · Contabilidad · Hermosillo", brand, size=40)
    # marca solo en el último segmento (cierre) — o aplicamos a todos vía concat
    lst = tmp / "list.txt"
    lst.write_text("\n".join(f"file '{s}'" for s in segs))
    concat = tmp / "concat.mp4"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(concat)],
                   capture_output=True, text=True)
    # overlay marca en cierre (últimos 3s) — simple: overlay en todo el video, esquina
    r = subprocess.run(
        ["ffmpeg", "-y", "-i", str(concat), "-i", str(brand), "-filter_complex",
         "[1:v]scale=500:-1[bm];[0:v][bm]overlay=30:80[out]",
         "-map", "[out]", "-c:v", "libx264", "-preset", "medium", "-crf", "23", str(OUT)],
        capture_output=True, text=True)
    if r.returncode != 0:
        print(f"✗ marca: {r.stderr[-300:]}")
        # al menos dejamos el concat
        OUT.write_bytes(concat.read_bytes())
    print(f"✅ Reel: {OUT} ({OUT.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())