"""Prompt Metrics - Métricas de calidad de prompts."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class PromptMetric:
    """Métrica de un prompt."""
    prompt_name: str
    metric_type: str  # "response_time", "accuracy", "consistency", "token_count"
    value: float
    unit: str = ""
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()


class PromptMetrics:
    """
    Prompt Metrics - Sistema de métricas para prompts.

    Rastrea:
    - Tiempo de respuesta
    - Precisión
    - Consistencia
    - Uso de tokens
    """

    def __init__(self):
        self.metrics: list[PromptMetric] = []

    def record(
        self,
        prompt_name: str,
        metric_type: str,
        value: float,
        unit: str = "",
    ):
        """Registra una métrica."""
        metric = PromptMetric(
            prompt_name=prompt_name,
            metric_type=metric_type,
            value=value,
            unit=unit,
        )
        self.metrics.append(metric)

    def get_metrics(
        self,
        prompt_name: Optional[str] = None,
        metric_type: Optional[str] = None,
    ) -> list[PromptMetric]:
        """Obtiene métricas filtradas."""
        results = self.metrics

        if prompt_name:
            results = [m for m in results if m.prompt_name == prompt_name]
        if metric_type:
            results = [m for m in results if m.metric_type == metric_type]

        return results

    def get_average(
        self,
        prompt_name: str,
        metric_type: str,
    ) -> float:
        """Obtiene el promedio de una métrica."""
        metrics = self.get_metrics(prompt_name, metric_type)
        if not metrics:
            return 0.0
        return sum(m.value for m in metrics) / len(metrics)

    def get_summary(self, prompt_name: str) -> dict:
        """Obtiene resumen de métricas para un prompt."""
        metrics = self.get_metrics(prompt_name)

        summary = {}
        for m in metrics:
            if m.metric_type not in summary:
                summary[m.metric_type] = {
                    "count": 0,
                    "total": 0,
                    "min": float('inf'),
                    "max": float('-inf'),
                }
            summary[m.metric_type]["count"] += 1
            summary[m.metric_type]["total"] += m.value
            summary[m.metric_type]["min"] = min(summary[m.metric_type]["min"], m.value)
            summary[m.metric_type]["max"] = max(summary[m.metric_type]["max"], m.value)

        # Calcular promedios
        for metric_type in summary:
            count = summary[metric_type]["count"]
            summary[metric_type]["avg"] = summary[metric_type]["total"] / count

        return summary

    def get_stats(self) -> dict:
        """Obtiene estadísticas generales."""
        total = len(self.metrics)
        types = set(m.metric_type for m in self.metrics)
        prompts = set(m.prompt_name for m in self.metrics)

        return {
            "total_metrics": total,
            "metric_types": list(types),
            "prompts_tracked": list(prompts),
        }
