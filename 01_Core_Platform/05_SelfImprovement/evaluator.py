"""Evaluator — LLM-judged scoring of task outputs.

Scores on 5 dimensions (1-10 each):
  - correctness  — does the output contain accurate information?
  - efficiency  — was the task completed without unnecessary steps?
  - clarity     — is the output clear and well-structured?
  - completeness — does the output address all parts of the task?
  - overall     — aggregate score (weighted average)

Also classifies failure_type when applicable.
"""

import json
import time
from dataclasses import dataclass
from typing import Optional

from sdc_sdk import call_llm
from experience_store import ExperienceStore

EVALUATOR_SYSTEM = """Eres un evaluador de IA imparcial. Calificas el rendimiento de agentes de IA
en tareas complejas. Usas una escala 1-10. Sé estricto pero justo. Siempre respondes
con JSON válido. Nunca des explicaciones fuera del JSON."""

EVALUATOR_PROMPT_TEMPLATE = """Evalúa esta tarea ejecutada por un agente de IA. Devuelve JSON con esta estructura exacta:

{{
  "correctness": <0-10>,
  "efficiency": <0-10>,
  "clarity": <0-10>,
  "completeness": <0-10>,
  "overall": <0-10>,
  "success_rate": <0-1>,
  "failure_type": "<none|cascade|hallucination|timeout|logic_error|incomplete|wrong_tool|other>",
  "notes": "<breve análisis en 1-2 frases>"
}}

TAREA: {task_type}
ENTRADA: {task_input}
SALIDA: {task_output}
DURACIÓN: {duration_ms}ms
ESTADO: {status}
AGENTE: {agent_id}
MODELO: {model}

Reglas:
- 10 = perfecto, 1 = gravemente defectuoso
- Si status=failure, overall debe ser ≤4
- success_rate = probabilidad de que la salida sea utilizable (0-1)
- failure_type: "none" si todo bien; si hay error, clasifícalo
- notes: máximo 200 caracteres"""


@dataclass
class EvaluationResult:
    task_id: str
    score: float
    success_rate: float
    correctness: float
    efficiency: float
    clarity: float
    completeness: float
    failure_type: str
    notes: str
    raw_response: str
    evaluator: str = "llm"
    timestamp: float = 0.0

    def __post_init__(self):
        if self.timestamp == 0:
            self.timestamp = time.time()
        if self.score == 0:
            self.score = sum([
                self.correctness, self.efficiency,
                self.clarity, self.completeness
            ]) / 4

    @property
    def is_success(self) -> bool:
        return self.score >= 7.0 and self.failure_type == "none"


class Evaluator:
    """LLM-judged evaluator for agent task outputs."""

    def __init__(self, store: Optional[ExperienceStore] = None, model: Optional[str] = None):
        self.store = store or ExperienceStore()
        self.model = model

    def evaluate(
        self,
        task_id: str,
        task_type: str,
        task_input: str,
        task_output: str,
        status: str = "success",
        duration_ms: int = 0,
        agent_id: str = "",
        model: str = "",
        max_retries: int = 2,
    ) -> EvaluationResult:
        """Evaluate a single task output using LLM judgment."""
        for attempt in range(max_retries + 1):
            try:
                prompt = EVALUATOR_PROMPT_TEMPLATE.format(
                    task_type=task_type,
                    task_input=task_input[:2000],
                    task_output=task_output[:3000],
                    duration_ms=duration_ms,
                    status=status,
                    agent_id=agent_id,
                    model=model,
                )

                result = call_llm(
                    prompt=prompt,
                    system=EVALUATOR_SYSTEM,
                    model=self.model,
                    max_tokens=1024,
                    temperature=0.3,
                )

                # parse JSON from LLM response
                parsed = self._parse_response(result)
                if parsed:
                    return self._build_result(task_id, parsed, result)

            except Exception as e:
                if attempt == max_retries:
                    return self._fallback_eval(
                        task_id, task_output, status, f"parse error after retries: {e}"
                    )

        return self._fallback_eval(
            task_id, task_output, status, "unexpected evaluator failure"
        )

    def _parse_response(self, raw: str) -> Optional[dict]:
        """Parse JSON from LLM response, handling fence artifacts."""
        raw = raw.strip()
        if raw.startswith("```json"):
            raw = raw[7:]
        if raw.startswith("```"):
            raw = raw[3:]
        raw = raw.rstrip("```").strip()
        try:
            data = json.loads(raw)
            required = ["correctness", "efficiency", "clarity", "completeness"]
            for key in required:
                if key not in data:
                    return None
            data.setdefault("overall", sum(data[k] for k in required) / 4)
            data.setdefault("success_rate", data["overall"] / 10)
            data.setdefault("failure_type", "none")
            data.setdefault("notes", "")
            return data
        except (json.JSONDecodeError, KeyError):
            return None

    def _build_result(self, task_id: str, parsed: dict, raw: str) -> EvaluationResult:
        return EvaluationResult(
            task_id=task_id,
            score=parsed["overall"],
            success_rate=parsed.get("success_rate", parsed["overall"] / 10),
            correctness=parsed["correctness"],
            efficiency=parsed["efficiency"],
            clarity=parsed["clarity"],
            completeness=parsed["completeness"],
            failure_type=parsed.get("failure_type", "none"),
            notes=parsed.get("notes", ""),
            raw_response=raw,
        )

    def _fallback_eval(self, task_id: str, output: str, status: str, reason: str) -> EvaluationResult:
        """Deterministic fallback: score based on output length + status."""
        base_score = 5.0
        if status == "success":
            base_score += min(2.0, len(output) / 200)
        else:
            base_score = 2.0
        return EvaluationResult(
            task_id=task_id,
            score=min(10.0, max(0.0, base_score)),
            success_rate=0.6 if status == "success" else 0.2,
            correctness=base_score,
            efficiency=base_score,
            clarity=base_score,
            completeness=base_score,
            failure_type="other" if status == "failure" else "none",
            notes=f"fallback evaluation: {reason}",
            raw_response="",
            evaluator="fallback",
        )

    def evaluate_and_store(self, **kwargs) -> EvaluationResult:
        """Evaluate a task and persist the result to the store."""
        result = self.evaluate(**kwargs)
        self.store.store_evaluation(
            task_id=result.task_id,
            score=result.score,
            success_rate=result.success_rate,
            correctness=result.correctness,
            efficiency=result.efficiency,
            clarity=result.clarity,
            completeness=result.completeness,
            failure_type=result.failure_type,
            notes=result.notes,
            evaluator=result.evaluator,
            raw_response=result.raw_response[:2000] if result.raw_response else None,
        )
        return result


__all__ = ["Evaluator", "EvaluationResult"]
