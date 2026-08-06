#!/usr/bin/env python3
"""Envío a Alex Usa: presentación PDF + slides del asistente de IA para RYE.

Renders alex_ai_deck.html (13 slides) → PNGs + PDF con playwright (chromium)
→ wacli send file a Alex.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

WACLI = os.environ.get("WACLI_PATH") or os.path.expanduser("~/.local/bin/wacli")
STORE = os.environ.get("WACLI_STORE") or os.path.expanduser("~/.wacli/accounts/personal")
TO_NUMBER = "12059021830"
DECK_HTML = Path(__file__).resolve().parent / "alex_ai_deck.html"

N_SLIDES = 13


def send_file(to: str, path: str, caption: str = "") -> dict:
    to = to if "@s.whatsapp.net" in to else f"{to}@s.whatsapp.net"
    cmd = [WACLI, "send", "file", "--file", path, "--caption", caption,
           "--to", to, "--post-send-wait", "3s", "--store", STORE, "--json"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    out = r.stdout.strip()
    return json.loads(out) if out else {"success": False, "error": r.stderr.strip()}


def render(out_dir: Path) -> tuple:
    """Renders slides PNG + PDF. Returns (slides, pdf_path)."""
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
    page.wait_for_timeout(500)
    for i in range({N_SLIDES}):
        page.locator('.slide').nth(i).screenshot(path=f'{{out}}/slide-{{i+1}}.png')
    pdf_path = f'{{out}}/presentacion_alex_ai.pdf'
    page.pdf(path=pdf_path, print_background=True, prefer_css_page_size=True)
    b.close()
"""
        subprocess.run([sys.executable, "-c", code], check=True, timeout=180)
    slides = [out_dir / f"slide-{i+1}.png" for i in range(N_SLIDES)]
    return slides, out_dir / "presentacion_alex_ai.pdf"


def main():
    out_dir = Path(tempfile.mkdtemp(prefix="alex_ai_deck_"))
    print(f"1/2 Renderizando slides y PDF...")
    slides, pdf_path = render(out_dir)
    print(f"    slides: {len(slides)} · pdf: {pdf_path.name} ({pdf_path.stat().st_size} bytes)")

    print(f"2/2 Enviando a Alex ({TO_NUMBER})...")
    r = send_file(TO_NUMBER, str(pdf_path),
                  "Tu asistente de producción — Sonora Digital Corp (PDF)")
    ok = r.get("success") or r.get("data", {}).get("sent")
    print(f"    PDF: {'OK' if ok else r}")

    for i, s in enumerate(slides, 1):
        r = send_file(TO_NUMBER, str(s), f"Tu asistente de producción ({i}/{len(slides)})")
        ok = r.get("success") or r.get("data", {}).get("sent")
        print(f"    slide {i}/{len(slides)}: {'OK' if ok else r}")


if __name__ == "__main__":
    main()
