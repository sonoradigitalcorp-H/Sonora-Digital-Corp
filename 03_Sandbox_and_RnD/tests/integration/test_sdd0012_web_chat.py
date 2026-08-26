#!/usr/bin/env python3
"""test_sdd0012_web_chat.py — Tests SDD-0012: soul cleaning, UI copy, contratos.
Corre en laptop (liviano, cero procesos pesados):
    python3 -m pytest 03_Sandbox_and_RnD/tests/integration/test_sdd0012_web_chat.py -v
"""
import importlib.util
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

AI_SERVER = ROOT / "01_Core_Platform" / "04_Automations_and_Workflows" / "vps_ai_server.py"
TTS_SERVER = ROOT / "01_Core_Platform" / "03_Agentic_Infrastructure" / "voice" / "tts_server.py"
UI = ROOT / "02_Client_Projects" / "Sonora_Digital_Corp" / "04_Deployment" / "chat_pro_max" / "index.html"


_CACHE = {}

def _load(name, path):
    # Cache: importar el server UNA sola vez por proceso. Re-importar vps_ai_server
    # re-ejecuta start_http_server + registra metricas de nuevo → prometheus DuplicateTimeseries.
    if name in _CACHE:
        return _CACHE[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    # Neutralizar start_http_server para no colisionar el registry de prometheus al importar
    import prometheus_client
    real_start = prometheus_client.start_http_server
    prometheus_client.start_http_server = lambda *a, **k: object()
    try:
        spec.loader.exec_module(mod)
    finally:
        prometheus_client.start_http_server = real_start
    _CACHE[name] = mod
    return mod


# ── Soul cleaning (server) ──────────────────────────────────
def test_clean_reply_sin_exclamaciones():
    mod = _load("vps", AI_SERVER)
    assert mod.clean_reply("Hola! Qué tal¡") == "Hola. Qué tal"
    assert "!" not in mod.clean_reply("Genial!!! Excelente!")


def test_clean_reply_colapsa_puntos_y_espacios():
    mod = _load("vps", AI_SERVER)
    out = mod.clean_reply("Uno.. Dos...   Tres")
    assert ".." not in out and "..." not in out


def test_forbidden_regex_detecta_tecnicismos():
    mod = _load("vps", AI_SERVER)
    for t in ("somos una IA", "nuestro agente", "usa un modelo LLM",
              "es un chatbot", "inteligencia artificial"):
        assert mod.FORBIDDEN_RE.search(t), f"debía detectar: {t}"


def test_soft_replace_elimina_tecnicismos():
    mod = _load("vps", AI_SERVER)
    out = mod.soft_replace_tech("Nuestro agente IA usa un modelo")
    assert not mod.FORBIDDEN_RE.search(out)


def test_souls_cumplen_reglas_duras():
    mod = _load("vps", AI_SERVER)
    for name, s in mod.SOULS.items():
        # exclamación USADA tras letra (no la mención en la regla "ni ¡ ni !")
        assert not re.search(r"[a-záéíóúñ]!\s|[a-záéíóúñ]!\.|¡[a-z]", s), \
            f"{name}: exclamación usada en soul"
        assert len(s) > 200, f"{name}: soul demasiado corto"
    # los fallbacks offline tampoco
    assert "!" not in mod.SOULS.get("_fallback", "")


# ── TTS clean (voice server) ────────────────────────────────
def test_tts_clean_quita_exclamaciones_y_emojis():
    tts = _load("tts", TTS_SERVER)
    out = tts.clean_for_tts("Hola! cómo estás 🎉 bien¡")
    assert "!" not in out and "¡" not in out
    assert "🎉" not in out


def test_voces_configuradas_por_persona():
    tts = _load("tts", TTS_SERVER)
    assert tts.VOICES["sdc"].startswith("es-MX")
    assert tts.VOICES["nathaly"].startswith("es-MX")


# ── UI Pro Max (estático) ───────────────────────────────────
@pytest.mark.skipif(not UI.exists(), reason="index.html no existe")
class TestUIProMax:
    html = UI.read_text() if UI.exists() else ""

    def test_sin_dashboard(self):
        low = self.html.lower()
        assert "dashboard" not in low
        # "admin" solo válido como parte de "administración" (servicio de Nathaly)
        assert not re.search(r"admin(?!istraci)", low), "panel admin detectado"
        assert 'id="panel"' not in low and "crm" not in low

    def test_personas_definidas(self):
        assert "sdc:" in self.html and "nathaly:" in self.html

    def test_endpoints_correctos(self):
        assert "/api/v1/chat/completions" in self.html
        assert "/api/stt" in self.html
        assert "/api/tts" in self.html

    def test_threejs_orbe_presente(self):
        assert "three.min.js" in self.html or "THREE." in self.html
        assert "IcosahedronGeometry" in self.html

    def test_glassmorphism_presente(self):
        assert "backdrop-filter" in self.html

    def test_mic_push_to_talk(self):
        assert "MediaRecorder" in self.html
        assert "getUserMedia" in self.html

    def test_stop_button(self):
        assert 'id="stopBtn"' in self.html

    def test_copy_hero_sin_exclamaciones(self):
        # extrae strings de P.sdc y P.nathaly del JS
        for m in re.finditer(r'"([^"\\]{10,})"', self.html):
            s = m.group(1)
            if any(k in s for k in ("empresa", "contabilidad", "horas")):
                assert "!" not in s, f"exclamación en copy UI: {s[:60]}"

    def test_sin_palabras_prohibidas_en_copy_visible(self):
        # el copy visible (hero/sub/greet/rail) no debe mencionar tecnología
        forbidden = re.compile(r"\b(inteligencia artificial|LLM|RAG|embedding|chatbot)\b", re.I)
        js_zone = self.html.split("const P = {")[1].split("/* ══════════════ THREE")[0]
        hits = [w.group(0) for w in forbidden.finditer(js_zone)]
        assert not hits, f"palabras prohibidas en copy: {hits}"

    def test_rail_value_samples(self):
        assert 'rail-title' in self.html and "Muestras de valor" in self.html

    def test_catalogo_asistentes_nichos(self):
        assert "catalogRail" in self.html and "catcard" in self.html
        # debe haber catálogo de nichos con beneficios/ahorro
        for k in ("Boutique", "Consultorio", "Restaurante", "Taller"):
            assert k in self.html, f"falta nicho {k} en catálogo"
        assert "Ahorra" in self.html  # mostrar ahorros

    def test_agenda_visible(self):
        assert "agendaOverlay" in self.html
        assert "/api/v1/citas" in self.html
        assert 'id="agFecha"' in self.html and 'id="agSlots"' in self.html
        assert "Confirmar cita" in self.html

    def test_comando_silencio(self):
        assert "SILENCE_RE" in self.html
        assert "stopSpeaking()" in self.html

    def test_mic_umbral_bajo(self):
        # umbral bajado para evitar "No escuché nada" falso
        assert "blob.size<300" in self.html
        assert "MediaRecorder" in self.html


def test_server_endpoints_registrados():
    mod = _load("vps", AI_SERVER)
    routes = {r.resource.canonical for r in mod.app.router.routes()}
    for path, meths in [("/api/v1/chat/completions", True), ("/api/stt", True),
                        ("/api/tts", True), ("/api/v1/citas", True)]:
        assert any(path in r for r in routes), f"falta ruta {path}"
    # wacli configurable por env
    assert "WACLI_BIN" in open(AI_SERVER).read() or "os.environ.get(\"WACLI_BIN" in open(AI_SERVER).read()


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
