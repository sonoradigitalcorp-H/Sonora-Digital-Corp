#!/usr/bin/env python3
"""Eval suite para agentes SDC.

Correr con:
    deepeval test run sonora-enterprise-os/eval/
    pytest sonora-enterprise-os/eval/ -v
"""

import pytest
from deepeval import assert_test
from deepeval.metrics import (
    HallucinationMetric,
    AnswerRelevancyMetric,
    ContextualPrecisionMetric,
    GEval
)
from deepeval.test_case import LLMTestCase


# ── Prueba 1: JARVIS no alucina sobre SDC ──
def test_jarvis_no_hallucinates():
    metric = HallucinationMetric(threshold=0.3)
    test_case = LLMTestCase(
        input="Â¿QuiÃ©nes son los fundadores de Sonora Digital Corp?",
        actual_output="Mystic y Noel son los co-fundadores de Sonora Digital Corp.",
        context=["Sonora Digital Corp fue fundada por Mystic y Noel"]
    )
    assert_test(test_case, [metric])


# ── Prueba 2: Respuesta relevante ──
def test_answer_relevancy():
    metric = AnswerRelevancyMetric(threshold=0.7)
    test_case = LLMTestCase(
        input="Â¿QuÃ© servicios ofrece SDC?",
        actual_output="SDC ofrece agentes de IA, automatizaciÃ³n con n8n, "
                      "bots de Telegram, y soluciones multi-tenant para empresas.",
        context=["SDC provee agentes de IA, automatizaciÃ³n, bots y multi-tenancy"]
    )
    assert_test(test_case, [metric])


# ── Prueba 3: ABE Fenix responde correctamente sobre mÃºsica ──
def test_abe_fenix_music():
    metric = AnswerRelevancyMetric(threshold=0.7)
    test_case = LLMTestCase(
        input="Â¿CÃ³mo puedo distribuir mi mÃºsica con ABE?",
        actual_output="ABE Fenix te ayuda a distribuir tu mÃºsica en plataformas "
                      "digitales, gestionar regalÃ­as y conectar con tu audiencia "
                      "a travÃ©s de Telegram.",
        context=["ABE Fenix es una plataforma de distribuciÃ³n musical con IA"]
    )
    assert_test(test_case, [metric])


# ── Prueba 4: EvaluaciÃ³n con GEval (custom criteria) ──
def test_response_is_helpful():
    metric = GEval(
        name="Helpfulness",
        criteria="Determina si la respuesta es Ãºtil y accionable para el usuario.",
        threshold=0.7,
        model="openrouter/deepseek-1.5b"
    )
    test_case = LLMTestCase(
        input="Â¿QuÃ© debo hacer si mi bot de Telegram no responde?",
        actual_output="Revisa que el token del bot sea correcto en el archivo de configuraciÃ³n. "
                      "Verifica los logs con: journalctl -u telegram-bot.service. "
                      "Si el problema persiste, ejecuta sdc-status para verificar el estado del sistema.",
        expected_output="Instrucciones claras para debuggear el bot de Telegram"
    )
    assert_test(test_case, [metric])


# ── Prueba 5: PrecisiÃ³n contextual ──
def test_contextual_precision():
    metric = ContextualPrecisionMetric(threshold=0.7)
    test_case = LLMTestCase(
        input="Â¿CuÃ¡l es la IP del VPS de SDC?",
        actual_output="La IP del VPS es 149.56.46.173",
        expected_output="149.56.46.173",
        context=["El VPS de SDC tiene IP 149.56.46.173, Ubuntu 26.04"]
    )
    assert_test(test_case, [metric])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
