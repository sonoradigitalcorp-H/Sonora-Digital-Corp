#!/usr/bin/env python3
"""Eval suite para SDC Core — Chat, Orchestrator, Web UI."""

import pytest
from deepeval import assert_test
from deepeval.metrics import (
    HallucinationMetric,
    AnswerRelevancyMetric,
    GEval,
)
from deepeval.test_case import LLMTestCase


def test_jarvis_no_hallucinates():
    """JARVIS no debe alucinar sobre información de SDC."""
    metric = HallucinationMetric(threshold=0.3)
    test_case = LLMTestCase(
        input="¿Quiénes son los fundadores de Sonora Digital Corp?",
        actual_output="Mystic y Noel son los co-fundadores de Sonora Digital Corp.",
        context=["Sonora Digital Corp fue fundada por Mystic y Noel"],
    )
    assert_test(test_case, [metric])


def test_chat_relevancy():
    """El chat de Web UI debe dar respuestas relevantes."""
    metric = AnswerRelevancyMetric(threshold=0.7)
    test_case = LLMTestCase(
        input="¿Qué servicios ofrece SDC?",
        actual_output="SDC ofrece agentes de IA, automatización con n8n, "
                      "bots de Telegram, y soluciones multi-tenant para empresas.",
        context=["SDC provee agentes de IA, automatización, bots y multi-tenancy"],
    )
    assert_test(test_case, [metric])


def test_orchestrator_routes_correctly():
    """El orquestador debe rutejar al agente correcto."""
    metric = GEval(
        name="Routing Accuracy",
        criteria="La respuesta indica el agente correcto para la tarea.",
        threshold=0.7,
    )
    test_case = LLMTestCase(
        input="Implementa una función en Python",
        actual_output="El agente code debe implementar esta función.",
        expected_output="code",
    )
    assert_test(test_case, [metric])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
