#!/usr/bin/env python3
"""Tests TDD del tenant hermosillo-cont (SDD 0006).

Cubre: routing, captura lead, scoring, agendamiento SAT (America/Hermosillo),
normalización de servicios, notificación Nathaly.
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from onboarding_hermosillo import OnboardingHermosillo, normalizar_servicio  # noqa: E402


class TestRouting(unittest.TestCase):
    """bot_name → tenant hermosillo-cont (refleja tenant_router.py)."""

    def test_router_mapping(self):
        import json
        from pathlib import Path
        registry = json.loads(Path(os.path.expanduser("~/.hermes/tenants/tenants.json")).read_text())
        hc = registry["tenants"]["hermosillo-cont"]
        self.assertEqual(hc["bot_name"], "HermosilloCont_bot")
        self.assertEqual(hc["owner"], "Nathaly")


class TestServicios(unittest.TestCase):
    def test_normalizar_aliases(self):
        self.assertEqual(normalizar_servicio("contabilidad"), "contabilidad")
        self.assertEqual(normalizar_servicio("llevo cuentas"), "contabilidad")
        self.assertEqual(normalizar_servicio("impuestos"), "contabilidad")
        self.assertEqual(normalizar_servicio("manifestacion de importacion"), "manifestacion_importacion")
        self.assertEqual(normalizar_servicio("cita ante el sat"), "citas_sat")
        self.assertEqual(normalizar_servicio("marketing"), "marketing")
        self.assertIsNone(normalizar_servicio("hola"))


class TestOnboarding(unittest.TestCase):
    def setUp(self):
        self.db = tempfile.mktemp(suffix=".db")
        self.eng = OnboardingHermosillo(self.db)

    def tearDown(self):
        if os.path.exists(self.db):
            os.remove(self.db)

    def test_registrar_lead(self):
        lead = self.eng.registrar_lead("111", {"nombre": "Ana", "negocio": "Café", "servicio": "contabilidad"})
        self.assertEqual(lead["tenant"], "hermosillo-cont")
        self.assertTrue(lead["id"])
        self.assertIn(lead["classification"], ("COLD", "WARM", "HOT"))

    def test_hot_lead(self):
        lead = self.eng.registrar_lead("222", {
            "nombre": "Pedro", "negocio": "Comercial X", "servicio": "citas_sat",
            "fecha": "2026-09-01", "hora": "10:00", "urgencia_alta": True,
            "presupuesto_mencionado": True, "es_tomador_decisiones": True,
        })
        self.assertEqual(lead["classification"], "HOT")

    def test_agendar_cita_ok(self):
        cita = self.eng.agendar_cita("333", "2026-08-30", "11:30")
        self.assertTrue(cita["ok"])
        self.assertEqual(cita["tz"], "America/Hermosillo")

    def test_agendar_cita_pasada(self):
        cita = self.eng.agendar_cita("444", "2020-01-01", "10:00")
        self.assertFalse(cita["ok"])

    def test_agendar_cita_formato_invalido(self):
        cita = self.eng.agendar_cita("555", "no-es-fecha", "xx")
        self.assertFalse(cita["ok"])

    def test_notificacion_nathaly(self):
        lead = self.eng.registrar_lead("666", {"nombre": "Luis", "negocio": "Taller", "servicio": "consultas_sat"})
        tmpl = self.eng.get_template_notificacion(lead)
        self.assertIn("LEAD", tmpl)
        self.assertIn("Luis", tmpl)

    def test_leads_hoy(self):
        """Registrar lead persiste y se recupera con score."""
        lead = self.eng.registrar_lead("777", {"nombre": "Sofi", "servicio": "marketing"})
        self.assertIsNotNone(lead.get("id"))
        self.assertIn("score", lead)


if __name__ == "__main__":
    unittest.main(verbosity=2)