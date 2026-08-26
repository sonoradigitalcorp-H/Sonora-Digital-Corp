"""TDD tests — Descontaminación páginas Pro Max (SPEC-0015).

Estos tests FALLAN ahora (bug real) y deben PASAR tras el fix.
Verifican contra la PRODUCCIÓN real del VPS (sin mocks).

Run:
    python3 -m pytest 03_Sandbox_and_RnD/tests/integration/test_paginas_pro_max.py -v
"""
import os
import subprocess

VPS = "149.56.46.173"
SSH_KEY = os.path.expanduser("~/.ssh/id_ed25519_sdc")
SSH_BASE = ["ssh", "-i", SSH_KEY, "-o", "IdentitiesOnly=yes",
            "-o", "ClearAllForwardings=yes", "-o", "BatchMode=yes", f"ubuntu@{VPS}"]
WWW = "/var/www/sonoradigitalcorp"

# Palabras que NUNCA deben aparecer en nathaly.html (contabilidad)
BANDERA_WORDS = ["adicciones", "12 Pasos", "tratamiento", "bandera", "fentanilo", "narcoticos"]
# Palabras que SÍ deben aparecer en nathaly.html
CONTAB_WORDS = ["contab", "sat", "impuestos", "declaracion", "nathaly"]


def ssh_content(path: str) -> str:
    r = subprocess.run(SSH_BASE + [f"cat {path} 2>/dev/null"],
                       capture_output=True, text=True, timeout=60)
    return r.stdout.lower()


def count_in(content: str, needle: str) -> int:
    return content.count(needle.lower())


class TestNathalyDescontaminacion:
    def test_sin_contenido_tubandera(self):
        content = ssh_content(f"{WWW}/nathaly.html")
        for w in BANDERA_WORDS:
            assert w.lower() not in content, f"nathaly.html aún contiene '{w}' (contaminación Tu Bandera)"

    def test_con_contenido_contabilidad(self):
        content = ssh_content(f"{WWW}/nathaly.html")
        hits = [w for w in CONTAB_WORDS if w in content]
        assert len(hits) >= 3, f"nathaly.html perdió su dominio contable: {hits}"


class TestIndexBugJS:
    def test_sin_lowercase_mal_escrito(self):
        content = ssh_content(f"{WWW}/index.html")
        assert ".lowercase()" not in content, "index.html tiene el bug c.n.lowerCase() (falta 'to')"


class TestTubanderaHonestidad:
    def test_fotos_no_vendidas_como_reales(self):
        content = ssh_content(f"{WWW}/tubandera.html")
        # No debe afirmar "fotos reales" para imágenes generadas por IA
        assert "fotos reales" not in content, "tubandera.html vende fotos IA como 'reales'"


class TestStackVozComun:
    def test_las_tres_conservan_voz(self):
        """Cada página debe conservar su stack de voz (MediaRecorder + STT + TTS)."""
        for page in ["index.html", "nathaly.html", "tubandera.html"]:
            content = ssh_content(f"{WWW}/{page}")
            assert "mediarecorder" in content, f"{page} perdió MediaRecorder"
            assert "/api/stt" in content or "speechsynthesis" in content, f"{page} perdió stack voz"
