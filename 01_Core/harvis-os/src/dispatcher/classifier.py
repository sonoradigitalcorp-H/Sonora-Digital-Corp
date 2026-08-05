"""Task classifier - Clasificación determinista de tareas."""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class ClassificationResult:
    """Resultado de clasificación."""
    category: str
    confidence: float
    routing_reason: str
    matched_pattern: Optional[str] = None


# Patrones de clasificación (deterministas - Principio II)
ROUTING_RULES = {
    "code": {
        "patterns": [
            r"código|code|programar|implementar|escribir|crear|desarrollar",
            r"función|function|clase|class|endpoint|api",
            r"bug|error|fix|arreglar|corregir",
            r"refactor|mejorar|optimizar",
            r"módulo|module|paquete|package",
        ],
        "agent": "openhands",
        "priority": "high",
        "base_confidence": 0.9,
    },
    "git": {
        "patterns": [
            r"git|commit|branch|merge|push|pull|repo",
            r"changelog|versión|release",
            r"stash|rebase|squash",
        ],
        "agent": "aider",
        "priority": "medium",
        "base_confidence": 0.85,
    },
    "query": {
        "patterns": [
            r"consultar|buscar|query|select|leer|ver|mostrar",
            r"¿qué|cuál|cuánto|dónde|cuándo",
            r"base de datos|database|tabla|table",
        ],
        "agent": "data_agent",
        "priority": "low",
        "base_confidence": 0.8,
    },
    "deploy": {
        "patterns": [
            r"deploy|desplegar|publicar|subir|lanzar",
            r"docker|container|servidor|server",
            r"nginx|apache|proxy",
        ],
        "agent": "openhands",
        "priority": "high",
        "base_confidence": 0.85,
    },
    "review": {
        "patterns": [
            r"revisar|review|audit|verificar|validar",
            r"prueba|test|testing",
            r"coverage|cobertura",
        ],
        "agent": "openhands",
        "priority": "medium",
        "base_confidence": 0.8,
    },
    "docs": {
        "patterns": [
            r"documentación|documentation|docs|readme",
            r"comentar|comment|explicar|explain",
            r"tutorial|guía|guide",
        ],
        "agent": "openhands",
        "priority": "low",
        "base_confidence": 0.75,
    },
}

# Fallback cuando no hay match
FALLBACK_RULE = {
    "category": "other",
    "agent": "planner",
    "priority": "low",
    "confidence": 0.5,
    "reason": "No pattern matched - fallback to planner",
}


class TaskClassifier:
    """Clasificador determinista de tareas (Principio II)."""

    def __init__(self):
        self.rules = ROUTING_RULES
        self.fallback = FALLBACK_RULE

    def classify(self, content: str) -> ClassificationResult:
        """
        Clasifica una tarea usando reglas deterministas.

        Args:
            content: Contenido de la tarea a clasificar

        Returns:
            ClassificationResult con categoría, confianza y razón
        """
        if not content or not content.strip():
            return ClassificationResult(
                category="invalid",
                confidence=0.0,
                routing_reason="Empty content",
            )

        content_lower = content.lower().strip()

        # Buscar match en cada categoría
        for category, rule in self.rules.items():
            for pattern in rule["patterns"]:
                if re.search(pattern, content_lower, re.IGNORECASE):
                    return ClassificationResult(
                        category=category,
                        confidence=rule["base_confidence"],
                        routing_reason=f"Pattern match: {pattern}",
                        matched_pattern=pattern,
                    )

        # Fallback a planner
        return ClassificationResult(
            category=self.fallback["category"],
            confidence=self.fallback["confidence"],
            routing_reason=self.fallback["reason"],
        )

    def get_agent_for_category(self, category: str) -> str:
        """Obtiene el agente recomendado para una categoría."""
        if category in self.rules:
            return self.rules[category]["agent"]
        return self.fallback["agent"]

    def get_priority_for_category(self, category: str) -> str:
        """Obtiene la prioridad para una categoría."""
        if category in self.rules:
            return self.rules[category]["priority"]
        return self.fallback["priority"]
