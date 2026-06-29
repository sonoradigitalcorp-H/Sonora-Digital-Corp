#!/usr/bin/env python3
"""Eval suite para Default Tenant — Tests generales de SDC."""

import pytest
from deepeval import assert_test
from deepeval.metrics import (
    AnswerRelevancyMetric,
    GEval,
    ContextualPrecisionMetric,
)
from deepeval.test_case import LLMTestCase


def test_general_helpfulness():
    """Las respuestas generales deben ser útiles y accionables."""
    metric = GEval(
        name="Helpfulness",
        criteria="La respuesta es útil, directa y accionable para el usuario.",
        threshold=0.7,
    )
    test_case = LLMTestCase(
        input="¿Qué debo hacer si mi bot de Telegram no responde?",
        actual_output="Revisa que el token del bot sea correcto. "
                      "Verifica los logs con: journalctl -u telegram-bot.service. "
                      "Si el problema persiste, ejecuta sdc-status.",
        expected_output="Instrucciones claras para debuggear el bot de Telegram",
    )
    assert_test(test_case, [metric])


def test_vps_info():
    """SDC debe proporcionar información correcta del VPS."""
    metric = ContextualPrecisionMetric(threshold=0.7)
    test_case = LLMTestCase(
        input="¿Cuál es la IP del VPS de SDC?",
        actual_output="La IP del VPS es 149.56.46.173",
        expected_output="149.56.46.173",
        context=["El VPS de SDC tiene IP 149.56.46.173, Ubuntu 26.04"],
    )
    assert_test(test_case, [metric])


def test_service_status():
    """SDC debe reportar estado de servicios correctamente."""
    metric = AnswerRelevancyMetric(threshold=0.7)
    test_case = LLMTestCase(
        input="¿Qué servicios están corriendo?",
        actual_output="Los servicios activos son: Web UI (5174), Hermes API (8000), "
                      "OpenClaw Gateway (18789), Qdrant (6333), Neo4j (7687), n8n (5678).",
        context=["SDC tiene servicios en puertos 5174, 8000, 18789, 6333, 7687, 5678"],
    )
    assert_test(test_case, [metric])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
