#!/usr/bin/env python3
"""Eval suite para ABE Fenix — Distribución musical, regalías, contratos."""

import pytest
from deepeval import assert_test
from deepeval.metrics import (
    AnswerRelevancyMetric,
    GEval,
    FaithfulnessMetric,
)
from deepeval.test_case import LLMTestCase


def test_music_distribution_info():
    """ABE Fenix debe responder correctamente sobre distribución musical."""
    metric = AnswerRelevancyMetric(threshold=0.7)
    test_case = LLMTestCase(
        input="¿Cómo puedo distribuir mi música con ABE?",
        actual_output="ABE Fenix te ayuda a distribuir tu música en plataformas "
                      "digitales, gestionar regalías y conectar con tu audiencia "
                      "a través de Telegram.",
        context=["ABE Fenix es una plataforma de distribución musical con IA"],
    )
    assert_test(test_case, [metric])


def test_royalty_calculation():
    """ABE Fenix debe calcular regalías correctamente."""
    metric = GEval(
        name="Royalty Accuracy",
        criteria="La respuesta contiene cálculos de regalías precisos y explicados.",
        threshold=0.7,
    )
    test_case = LLMTestCase(
        input="¿Cuánto gané en streaming este mes?",
        actual_output="Según tus datos, tus regalías de streaming este mes son $450 MXN.",
        expected_output="$450 MXN en regalías de streaming",
    )
    assert_test(test_case, [metric])


def test_contract_extraction():
    """ABE Fenix debe extraer información de contratos correctamente."""
    metric = FaithfulnessMetric(threshold=0.7)
    test_case = LLMTestCase(
        input="¿Qué dice mi contrato de distribución?",
        actual_output="Tu contrato establece un 85% de regalías para el artista, "
                      "con pagos trimestrales y distribución en 150+ plataformas.",
        context=["El contrato de distribución ABE Fenix establece 85% regalías artista"],
    )
    assert_test(test_case, [metric])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
