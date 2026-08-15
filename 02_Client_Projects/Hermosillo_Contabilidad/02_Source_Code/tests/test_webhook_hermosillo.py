#!/usr/bin/env python3
"""Tests del webhook Telegram Hermosillo Cont (SDD 0006 T1.5).

Prueba handle_update() sin red real: mockea telegram_call y el clasificador
para validar el enrutamiento de acciones y las respuestas.
"""

import sys
import json
import unittest
from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock, patch

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

import telegram_webhook_hermosillo as wh


def fake_telegram_call(method, payload):
    """Mock: registra llamadas a Telegram en vez de enviar."""
    fake_telegram_call.calls.append({"method": method, "payload": payload})
    return {"ok": True}


fake_telegram_call.calls = []


class TestWebhookHermosillo(unittest.TestCase):

    def setUp(self):
        fake_telegram_call.calls = []

    @patch.object(wh, "telegram_call", side_effect=fake_telegram_call)
    @patch.object(wh, "classify_intent_hermosillo")
    def test_saludo_responde(self, mock_cls, mock_tg):
        mock_cls.return_value = wh.LeadClassificationHC(
            intencion="saludo", campos={}, confianza=0.98,
            respuesta_sugerida="¡Hola! ¿En qué te ayudo?",
            accion_requerida="responder")
        update = {"message": {"chat": {"id": 111}, "text": "hola"}}
        result = wh.handle_update(update)
        self.assertTrue(result["ok"])
        # Debe responder al chat 111 con la sugerida
        self.assertEqual(mock_tg.call_args[0][1]["chat_id"], 111)
        self.assertEqual(mock_tg.call_args[0][1]["text"], "¡Hola! ¿En qué te ayudo?")

    @patch.object(wh, "telegram_call", side_effect=fake_telegram_call)
    @patch.object(wh, "classify_intent_hermosillo")
    def test_capture_registra_lead(self, mock_cls, mock_tg):
        mock_cls.return_value = wh.LeadClassificationHC(
            intencion="nuevo_lead", campos={"nombre": "Juan", "negocio": "Ferret", "servicio": "contabilidad"},
            confianza=0.9, respuesta_sugerida="Cuéntame más",
            accion_requerida="capture")
        update = {"message": {"chat": {"id": 222}, "text": "necesito contabilidad"}}
        result = wh.handle_update(update)
        self.assertTrue(result["ok"])
        self.assertIn("lead", result)
        self.assertEqual(result["lead"]["nombre"], "Juan")
        self.assertEqual(mock_tg.call_args[0][1]["chat_id"], 222)

    @patch.object(wh, "telegram_call", side_effect=fake_telegram_call)
    @patch.object(wh, "classify_intent_hermosillo")
    def test_schedule_agenda_cita(self, mock_cls, mock_tg):
        mock_cls.return_value = wh.LeadClassificationHC(
            intencion="agendar_cita_sat",
            campos={"nombre": "María", "fecha": "2026-08-20", "hora": "10:30", "servicio": "citas_sat"},
            confianza=0.95, respuesta_sugerida="Te agendo",
            accion_requerida="schedule")
        update = {"message": {"chat": {"id": 333}, "text": "cita SAT mañana 10:30"}}
        result = wh.handle_update(update)
        self.assertTrue(result["ok"])
        self.assertIn("cita", result)
        # La cita se agenda y se responde al chat
        last = fake_telegram_call.calls[-1]["payload"]
        self.assertEqual(last["chat_id"], 333)

    @patch.object(wh, "telegram_call", side_effect=fake_telegram_call)
    @patch.object(wh, "classify_intent_hermosillo")
    def test_sin_texto_no_responde(self, mock_cls, mock_tg):
        update = {"message": {"chat": {"id": 444}, "text": ""}}
        result = wh.handle_update(update)
        self.assertFalse(result["ok"])
        self.assertEqual(mock_tg.call_count, 0)


if __name__ == "__main__":
    unittest.main()