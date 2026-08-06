"""Prompt Optimizer - Optimización de prompts."""

from dataclasses import dataclass, field
from typing import Any, Optional
import re


@dataclass
class OptimizationSuggestion:
    """Sugerencia de optimización."""
    type: str  # "length", "clarity", "specificity", "structure"
    description: str
    original: str
    suggested: str
    impact: str  # "high", "medium", "low"


class PromptOptimizer:
    """
    Prompt Optimizer - Optimiza prompts para mejor rendimiento.

    Analiza prompts y sugiere mejoras basadas en:
    - Longitud
    - Claridad
    - Especificidad
    - Estructura
    """

    def __init__(self):
        self.suggestions: list[OptimizationSuggestion] = []

    def analyze(self, prompt: str) -> dict:
        """
        Analiza un prompt y retorna métricas.

        Returns:
            Dict con métricas del prompt
        """
        words = prompt.split()
        sentences = re.split(r'[.!?]+', prompt)
        questions = prompt.count('?')

        return {
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "question_count": questions,
            "avg_word_length": sum(len(w) for w in words) / len(words) if words else 0,
            "has_variables": bool(re.search(r'\{(\w+)\}', prompt)),
            "has_examples": "example" in prompt.lower() or "e.g." in prompt.lower(),
            "has_constraints": any(w in prompt.lower() for w in ["must", "should", "always", "never"]),
            "complexity": self._calculate_complexity(prompt),
        }

    def optimize(self, prompt: str) -> list[OptimizationSuggestion]:
        """
        Optimiza un prompt y retorna sugerencias.

        Returns:
            Lista de sugerencias
        """
        suggestions = []

        # Check length
        if len(prompt) > 500:
            suggestions.append(OptimizationSuggestion(
                type="length",
                description="Prompt is too long. Consider breaking it into smaller parts.",
                original=prompt[:100] + "...",
                suggested="Break into multiple prompts or use variables",
                impact="high",
            ))

        # Check clarity
        if "?" not in prompt:
            suggestions.append(OptimizationSuggestion(
                type="clarity",
                description="No clear question or instruction. Add a specific question.",
                original=prompt[:100],
                suggested="Add 'What is...' or 'How to...' at the beginning",
                impact="medium",
            ))

        # Check specificity
        vague_words = ["thing", "stuff", "something", "anything", "good", "bad"]
        found_vague = [w for w in vague_words if w in prompt.lower()]
        if found_vague:
            suggestions.append(OptimizationSuggestion(
                type="specificity",
                description=f"Vague terms found: {found_vague}",
                original=prompt[:100],
                suggested="Replace vague terms with specific ones",
                impact="high",
            ))

        # Check structure
        if not prompt.startswith(("#", "You are", "Act as", "Given")):
            suggestions.append(OptimizationSuggestion(
                type="structure",
                description="Prompt doesn't start with a clear role or context.",
                original=prompt[:100],
                suggested="Start with 'You are a...' or 'Given {context}...'",
                impact="medium",
            ))

        # Check examples
        if "example" not in prompt.lower() and len(prompt) > 100:
            suggestions.append(OptimizationSuggestion(
                type="clarity",
                description="No examples provided. Examples improve accuracy.",
                original=prompt[:100],
                suggested="Add 'Example: input -> output' at the end",
                impact="medium",
            ))

        self.suggestions.extend(suggestions)
        return suggestions

    def _calculate_complexity(self, prompt: str) -> str:
        """Calcula la complejidad del prompt."""
        words = prompt.split()
        if len(words) < 10:
            return "low"
        elif len(words) < 50:
            return "medium"
        else:
            return "high"

    def get_stats(self) -> dict:
        """Obtiene estadísticas de optimización."""
        return {
            "total_suggestions": len(self.suggestions),
            "by_type": self._count_by_type(),
            "by_impact": self._count_by_impact(),
        }

    def _count_by_type(self) -> dict:
        counts = {}
        for s in self.suggestions:
            counts[s.type] = counts.get(s.type, 0) + 1
        return counts

    def _count_by_impact(self) -> dict:
        counts = {}
        for s in self.suggestions:
            counts[s.impact] = counts.get(s.impact, 0) + 1
        return counts
