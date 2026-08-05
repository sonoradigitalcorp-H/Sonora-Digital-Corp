"""Prompt Evaluator - Evaluación de prompts."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Optional
from uuid import uuid4
import re


@dataclass
class EvalCase:
    """Caso de evaluación."""
    id: str
    input_text: str
    expected_output: str
    expected_contains: list[str] = field(default_factory=list)
    expected_not_contains: list[str] = field(default_factory=list)
    expected_regex: Optional[str] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class EvalResult:
    """Resultado de evaluación."""
    id: str
    case_id: str
    prompt_name: str
    input_text: str
    actual_output: str
    expected_output: Optional[str]
    passed: bool
    score: float  # 0.0 - 1.0
    checks: dict = field(default_factory=dict)
    duration: float = 0.0
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()


class PromptEvaluator:
    """
    Prompt Evaluator - Evalúa la calidad de prompts.

    Permite:
    - Definir casos de prueba
    - Evaluar prompts contra casos
    - Medir calidad y consistencia
    - Detectar regresiones
    """

    def __init__(self):
        self.cases: dict[str, EvalCase] = {}
        self.results: list[EvalResult] = []
        self.prompts: dict[str, Callable] = {}

    def register_prompt(self, name: str, prompt_fn: Callable):
        """Registra un prompt para evaluación."""
        self.prompts[name] = prompt_fn

    def add_case(
        self,
        input_text: str,
        expected_output: str = None,
        expected_contains: list[str] = None,
        expected_not_contains: list[str] = None,
        expected_regex: str = None,
        metadata: dict = None,
    ) -> str:
        """
        Agrega un caso de evaluación.

        Returns:
            ID del caso creado
        """
        case_id = str(uuid4())
        case = EvalCase(
            id=case_id,
            input_text=input_text,
            expected_output=expected_output,
            expected_contains=expected_contains or [],
            expected_not_contains=expected_not_contains or [],
            expected_regex=expected_regex,
            metadata=metadata or {},
        )
        self.cases[case_id] = case
        return case_id

    def evaluate(
        self,
        prompt_name: str,
        input_text: str,
        expected_output: str = None,
        **kwargs,
    ) -> EvalResult:
        """
        Evalúa un prompt con una entrada específica.

        Args:
            prompt_name: Nombre del prompt registrado
            input_text: Texto de entrada
            expected_output: Salida esperada

        Returns:
            EvalResult con el resultado
        """
        import time
        start = time.time()

        if prompt_name not in self.prompts:
            raise ValueError(f"Prompt '{prompt_name}' not registered")

        # Ejecutar prompt
        prompt_fn = self.prompts[prompt_name]
        actual_output = prompt_fn(input_text)

        # Verificar resultado
        checks = {}
        passed = True

        # Check exact match
        if expected_output:
            checks["exact_match"] = actual_output == expected_output
            passed = passed and checks["exact_match"]

        # Check contains
        for term in kwargs.get("expected_contains", []):
            check_name = f"contains_{term[:20]}"
            checks[check_name] = term in actual_output
            passed = passed and checks[check_name]

        # Check not contains
        for term in kwargs.get("expected_not_contains", []):
            check_name = f"not_contains_{term[:20]}"
            checks[check_name] = term not in actual_output
            passed = passed and checks[check_name]

        # Check regex
        if kwargs.get("expected_regex"):
            checks["regex_match"] = bool(re.search(kwargs["expected_regex"], actual_output))
            passed = passed and checks["regex_match"]

        # Calcular score
        total_checks = len(checks)
        passed_checks = sum(1 for v in checks.values() if v)
        score = passed_checks / total_checks if total_checks > 0 else 1.0

        duration = time.time() - start

        result = EvalResult(
            id=str(uuid4()),
            case_id="manual",
            prompt_name=prompt_name,
            input_text=input_text,
            actual_output=actual_output,
            expected_output=expected_output,
            passed=passed,
            score=score,
            checks=checks,
            duration=duration,
        )

        self.results.append(result)
        return result

    def evaluate_case(self, prompt_name: str, case_id: str) -> EvalResult:
        """Evalúa un prompt contra un caso registrado."""
        if case_id not in self.cases:
            raise ValueError(f"Case '{case_id}' not found")

        case = self.cases[case_id]
        return self.evaluate(
            prompt_name,
            case.input_text,
            expected_output=case.expected_output,
            expected_contains=case.expected_contains,
            expected_not_contains=case.expected_not_contains,
            expected_regex=case.expected_regex,
        )

    def run_all(self, prompt_name: str) -> list[EvalResult]:
        """Ejecuta todos los casos para un prompt."""
        results = []
        for case_id in self.cases:
            result = self.evaluate_case(prompt_name, case_id)
            results.append(result)
        return results

    def get_stats(self) -> dict:
        """Obtiene estadísticas de evaluación."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        avg_score = sum(r.score for r in self.results) / total if total > 0 else 0

        return {
            "total_evaluations": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": passed / total if total > 0 else 0,
            "avg_score": avg_score,
        }
