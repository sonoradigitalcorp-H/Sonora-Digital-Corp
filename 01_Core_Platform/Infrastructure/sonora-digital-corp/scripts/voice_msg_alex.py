#!/usr/bin/env python3
"""Envío a Alex Usa: nota de voz (análisis financiero) + presentación de slides.

Pipeline de audio CORRECTO en scripts/voice_note.py (edge-tts → resample 16k → OGG/Opus).
Slides: deck.html → 7 PNG con playwright → wacli send file.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from scripts.voice_note import make_voice_note  # noqa: E402

WACLI = os.environ.get("WACLI_PATH") or os.path.expanduser("~/.local/bin/wacli")
STORE = os.environ.get("WACLI_STORE") or os.path.expanduser("~/.wacli/accounts/personal")
TO_NUMBER = "12059021830"

DECK_HTML = Path(__file__).resolve().parent / "alex_deck.html"

SCRIPT = (
    "Hola Alex, soy Mystic, la asistente de Perroni. Va carnal, ya analizamos tu situación completa. "
    "Revisamos las tres opciones: la casa de trescientos mil dólares te costaría casi dos mil al mes de tu bolsillo. "
    "En cambio, la propiedad de seiscientos mil con las nueve unidades, si la due diligence sale bien, "
    "te genera flujo neto de unos mil cuatrocientos sesenta y seis dólares al mes, y el mortgage se paga solo con las rentas. "
    "El cap rate del quince por ciento bruto está muy por encima del promedio en Estados Unidos. "
    "Te mandé también una presentación con todo el análisis en números y el checklist de lo que hay que revisar antes de comprometerte: "
    "el zoning multifamily, el título limpio, medidores de luz separados, y que las nueve unidades estén rentadas de verdad con contratos vigentes. "
    "Cuando quieras agendamos la llamada para la retro completa y te pasamos el proyecto de Perroni. Aquí andamos al tiro."
)


def send_file(to: str, path: str, caption: str = "") -> dict:
    to = to if "@s.whatsapp.net" in to else f"{to}@s.whatsapp.net"
    import json
    cmd = [WACLI, "send", "file", "--file", path, "--caption", caption,
           "--to", to, "--post-send-wait", "3s", "--store", STORE, "--json"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    out = r.stdout.strip()
    return json.loads(out) if out else {"success": False, "error": r.stderr.strip()}


def render_slides(out_dir: Path) -> list:
    slides = []
    with tempfile.TemporaryDirectory() as td:
        deck = Path(td) / "deck.html"
        deck.write_text(DECK_HTML.read_text())
        code = f"""
from playwright.sync_api import sync_playwright
import sys
out = {str(out_dir)!r}
with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page(viewport={{'width':1280,'height':720}})
    page.goto('file://{deck}')
    for i in range(7):
        page.locator('.slide').nth(i).screenshot(path=f'{{out}}/slide-{{i+1}}.png')
    b.close()
"""
        subprocess.run([sys.executable, "-c", code], check=True, timeout=120)
    for i in range(7):
        slides.append(out_dir / f"slide-{i+1}.png")
    return slides


def main():
    out_dir = Path(tempfile.mkdtemp(prefix="alex_deck_"))
    print(f"1/2 Enviando nota de voz...")
    result = make_voice_note(SCRIPT, TO_NUMBER)
    sent = result.get("success") or result.get("data", {}).get("sent")
    print(f"    nota de voz: {'OK' if sent else result}")

    print(f"2/2 Renderizando y enviando slides...")
    slides = render_slides(out_dir)
    for i, s in enumerate(slides, 1):
        r = send_file(TO_NUMBER, str(s), f"Tu análisis — Alex ({i}/7)")
        ok = r.get("success") or r.get("data", {}).get("sent")
        print(f"    slide {i}/7: {'OK' if ok else r}")


if __name__ == "__main__":
    main()
