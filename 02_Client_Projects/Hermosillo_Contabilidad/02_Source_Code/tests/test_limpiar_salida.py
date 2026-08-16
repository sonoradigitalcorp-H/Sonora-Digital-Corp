#!/usr/bin/env python3
"""Tests de limpiar_salida: respuestas SIN emojis, asteriscos ni signos de admiración/interrogación.
Cubre el requisito del cliente: texto entregado limpio y profesional (voz y web)."""

import sys
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

import telegram_webhook_hermosillo as wh


class TestLimpiarSalida(unittest.TestCase):

    def test_quita_emojis(self):
        out = wh.limpiar_salida("¡Hola Carlos! 😊 🧮 📊")
        for emoji in ["😊", "🧮", "📊"]:
            self.assertNotIn(emoji, out)

    def test_quita_asteriscos_y_markdown(self):
        out = wh.limpiar_salida("**Contabilidad** *IVA* `ISR`")
        self.assertNotIn("*", out)
        self.assertNotIn("`", out)

    def test_quita_signos_admiracion(self):
        out = wh.limpiar_salida("¡Exacto! ¿Qué necesitas?")
        self.assertNotIn("!", out)
        self.assertNotIn("?", out)
        self.assertNotIn("¡", out)
        self.assertNotIn("¿", out)

    def test_normaliza_espacios(self):
        out = wh.limpiar_salida("hola   mundo ,  amigo")
        self.assertNotIn("  ", out)

    def test_termina_en_punto(self):
        out = wh.limpiar_salida("te ayudo con contabilidad")
        self.assertTrue(out.endswith("."))

    def test_vacio_no_rompe(self):
        self.assertEqual(wh.limpiar_salida(""), "")
        self.assertEqual(wh.limpiar_salida(None), None)

    def test_doble_admiracion_se_colapsa(self):
        out = wh.limpiar_salida("¡¡Genial!!")
        self.assertNotIn("!", out)
        self.assertNotIn("¡", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)