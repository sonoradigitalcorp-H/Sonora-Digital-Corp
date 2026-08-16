#!/usr/bin/env python3
"""gen_canva_images.py — Genera imágenes estilo Canva (gráficos planos, SIN personas)
para el carrusel de la landing Hermosillo. Ilustran el servicio sin mostrar caras.

Estilo: flat design, gradientes suaves, iconos grandes, tipografía bold.
Uso: python3 gen_canva_images.py [--out DIR]
"""

import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
OUT = Path(sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else BASE / ".." / "03_Media_Assets" / "canva")
W, H = 1024, 1024
PAD = 60


def font(sz):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        try:
            return ImageFont.truetype(p, sz)
        except Exception:
            continue
    return ImageFont.load_default()


def bg_grad(d, c1, c2):
    """Gradiente vertical suave."""
    for y in range(H):
        t = y / H
        c = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)


def card_icon(d, cx, cy, r, color, shape="circle"):
    if shape == "circle":
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
    else:
        d.rounded_rectangle([cx - r, cy - r, cx + r, cy + r], radius=24, fill=color)


def draw_text_center(d, text, y, size, fill=(255, 255, 255, 255)):
    f = font(size)
    bbox = d.textbbox((0, 0), text, font=f)
    w = bbox[2] - bbox[0]
    d.text(((W - w) / 2, y), text, font=f, fill=fill)


SCENES = [
    # (nombre, c1, c2, icono, título, subtítulo, acentos)
    ("contabilidad", (14, 138, 109), (10, 74, 60), "📊",
     "CONTABILIDAD EN ORDEN", "Estados financieros · IVA · ISR al día", (255, 255, 255)),
    ("citas_sat", (14, 165, 233), (7, 70, 120), "🗓️",
     "CITAS SAT GESTIONADAS", "Agendamos y te acompañamos", (255, 255, 255)),
    ("declaracion", (109, 40, 217), (55, 20, 110), "🧾",
     "DECLARACIONES SIN ERRORES", "Cumplimiento fiscal sin multas", (255, 255, 255)),
    ("importacion", (245, 158, 11), (120, 60, 5), "🚢",
     "IMPORTACIONES EN REGLA", "Manifestación y requisitos", (255, 255, 255)),
    ("dashboard", (236, 72, 153), (110, 30, 70), "📈",
     "TU NEGOCIO EN TIEMPO REAL", "Dashboard claro y actualizado", (255, 255, 255)),
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, c1, c2, icon, title, sub, _ in SCENES:
        img = Image.new("RGB", (W, H))
        d = ImageDraw.Draw(img)
        bg_grad(d, c1, c2)
        # círculos decorativos estilo Canva
        d.ellipse([-150, -150, 250, 250], fill=(255, 255, 255, 0), outline=(255, 255, 255, 40), width=2)
        d.ellipse([W - 250, H - 250, W + 150, H + 150], fill=(255, 255, 255, 0), outline=(255, 255, 255, 40), width=2)
        # tarjeta central glass
        card_icon(d, W // 2, H // 2 - 60, 110, (255, 255, 255, 235), shape="circle")
        f_ic = font(90)
        bbox = d.textbbox((0, 0), icon, font=f_ic)
        d.text((W // 2 - (bbox[2] - bbox[0]) / 2, H // 2 - 60 - (bbox[3] - bbox[1]) / 2 - 40), icon, font=f_ic, fill=(30, 30, 30))
        # título
        draw_text_center(d, title, H // 2 + 130, 56)
        # subtítulo
        f_sub = font(32)
        bbox = d.textbbox((0, 0), sub, font=f_sub)
        d.text(((W - (bbox[2] - bbox[0])) / 2, H // 2 + 220), sub, font=f_sub, fill=(230, 240, 235))
        # marca
        f_m = font(26)
        d.text((PAD, H - PAD - 30), "Nathaly · Contabilidad · Hermosillo", font=f_m, fill=(255, 255, 255, 220))
        img.save(OUT / f"{name}.jpg", quality=88)
        print(f"✓ {name}.jpg")
    print(f"Listo en {OUT}")


if __name__ == "__main__":
    main()