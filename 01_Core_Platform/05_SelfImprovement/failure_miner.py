"""Failure Miner — extract patterns from failed tasks and generate insights.

Mining strategies:
  1. Length-based: output too short → "incomplete"
  2. Structure-based: detect missing JSON, missing steps, etc.
  3. Semantic clustering: group failures by failure_type
  4. Time-based: failures that recur after certain times (fatigue)
  5. Skill-based: failures grouped by skill/task_type
"""

import json
import re
import time
from dataclasses import dataclass, field
from typing import Optional
from collections import defaultdict

from sdc_sdk import call_llm, log_action
from experience_store import ExperienceStore

MINING_PROMPT = """Analiza este conjunto de fallas de tareas de agentes de IA. Extrae patrones
recurrentes y genera insights accionables.

Patrones a buscar:
1. Errores de lógica (cálculos incorrectos, pasos faltantes)
2. Alucinaciones (información inventada)
3. Falencias de herramientas (usar la herramienta equivocada)
4. Timeout / incompletos (respuesta truncada)
5. Errores de contexto (olvidar instrucciones previas)
6. Problemas de modelo (errores consistentes con un modelo específico)

Para cada patrón: type, description, skill_name (if applicable), confidence (0-1)
Para cada insight: description, recommendation, impact_score (1-10)

Formato respuesta: JSON.
{
  "patterns": [
    {"type": "...", "description": "...", "skill_name": "...", "confidence": 0.8}
  ],
  "insights": [
    {"description": "...", "recommendation": "...", "impact_score": 8.5}
  ]
}

DATOS DE FALLAS:
{failures_json}"""


@dataclass
class Pattern:
    type: str
    description: str
    skill_name: Optional[str]
    confidence: float
    frequency: int = 1
    first_seen: float = 0.0
    last_seen: float = 0.0

    def __post_init__(self):
        if self.first_seen == 0:
            self.first_seen = self.last_seen = time.time()


@dataclass
class Insight:
    description: str
    recommendation: str
    impact_score: float
    pattern_ids: list = field(default_factory=list)


class FailureMiner:
    """Mine patterns from task failures and generate insights."""

    def __init__(self, store: Optional[ExperienceStore] = None, model: Optional[str] = None):
        self.store = store or ExperienceStore()
        self.model = model

    def mine_deterministic(self, limit: int = 200) -> list[Pattern]:
        """Rule-based pattern extraction (no LLM needed)."""
        failures = self.store.get_failures(limit=limit)
        patterns: dict[str, Pattern] = {}

        for f in failures:
            pattern_key = None

            # Rule 1: Short output → incomplete
            out_len = len(f.get("output", ""))
            if out_len < 20 and f.get("status") == "failure":
                pattern_key = "incomplete_short_output"

            # Rule 2: No output → empty response
            elif not f.get("output", "").strip():
                pattern_key = "empty_output"

            # Rule 3: Very fast failure → tool error
            duration = f.get("duration_ms", 0) or 0
            if duration < 500 and f.get("status") == "failure":
                if pattern_key is None:
                    pattern_key = "rapid_tool_failure"

            # Rule 4: Grouped by failure_type from evaluation
            failure_type = (f.get("failure_type") or "").strip()
            if failure_type and failure_type != "none":
                pattern_key = f"failure_type:{failure_type}"

            if pattern_key:
                pid = hash(pattern_key) % 1000000
                if pid in patterns:
                    patterns[pid].frequency += 1
                    patterns[pid].last_seen = f.get("timestamp", time.time())
                    patterns[pid].confidence = min(1.0, patterns[pid].confidence + 0.05)
                else:
                    patterns[pid] = Pattern(
                        type=pattern_key.split(":")[0] if ":" in pattern_key else pattern_key,
                        description=pattern_key,
                        skill_name=f.get("type", ""),
                        confidence=0.1,
                        frequency=1,
                        first_seen=f.get("timestamp", time.time()),
                        last_seen=f.get("timestamp", time.time()),
                    )

        # Store patterns in DB
        for p in patterns.values():
            self.store.add_pattern(
                pattern_type=p.type,
                description=p.description,
                skill_name=p.skill_name,
                metadata={
                    "frequency": p.frequency,
                    "confidence": p.confidence,
                    "first_seen": p.first_seen,
                    "last_seen": p.last_seen,
                },
            )

        log_action("failure_mining_complete", metadata={"patterns_found": len(patterns)})
        return list(patterns.values())

    def mine_llm(self, limit: int = 50) -> tuple[list[Pattern], list[Insight]]:
        """LLM-based semantic pattern mining from recent failures."""
        failures = self.store.get_failures(limit=limit)
        if not failures:
            return [], []

        failures_json = json.dumps(failures, indent=2, default=str)
        prompt = MINING_PROMPT.format(failures_json=failures_json)

        try:
            result = call_llm(
                prompt=prompt,
                system="Eres un analista de fallos de IA. Devuelve JSON válido.",
                model=self.model,
                max_tokens=3000,
                temperature=0.2,
            )
            parsed = self._parse_mining_response(result)
            patterns, insights = [], []
            for p in parsed.get("patterns", []):
                patterns.append(Pattern(
                    type=p["type"],
                    description=p["description"],
                    skill_name=p.get("skill_name"),
                    confidence=p.get("confidence", 0.1),
                ))
                self.store.add_pattern(
                    pattern_type=p["type"],
                    description=p["description"],
                    skill_name=p.get("skill_name"),
                    metadata={"confidence": p.get("confidence", 0.1)},
                )
            for i in parsed.get("insights", []):
                insights.append(Insight(
                    description=i["description"],
                    recommendation=i["recommendation"],
                    impact_score=i.get("impact_score", 5.0),
                ))
            return patterns, insights
        except Exception as e:
            log_action("mining_failed", metadata={"error": str(e)})
            return [], []

    def _parse_mining_response(self, raw: str) -> dict:
        raw = raw.strip()
        if raw.startswith("```json"):
            raw = raw[7:]
        if raw.startswith("```"):
            raw = raw[3:]
        raw = raw.rstrip("```").strip()
        return json.loads(raw)

    def generate_insights(self) -> list[Insight]:
        """Generate insights from stored patterns."""
        patterns = self.store.get_patterns(min_confidence=0.3)
        if not patterns:
            return []

        # Group patterns by type
        by_type: dict[str, list] = defaultdict(list)
        for p in patterns:
            by_type[p["type"]].append(p)

        insights: list[Insight] = []

        for ptype, plist in by_type.items():
            total_freq = sum(p["frequency"] for p in plist)
            avg_conf = sum(p["confidence"] for p in plist) / len(plist)

            if ptype == "incomplete" or ptype == "incomplete_short_output":
                insights.append(Insight(
                    description=f"{total_freq} tareas incompletas detectadas en {len(plist)} skills",
                    recommendation="Añadir verificación de completitud antes de retornar. Forzar output mínimo de 50 caracteres.",
                    impact_score=min(9.0, total_freq * 0.5 + avg_conf * 5),
                ))

            elif ptype == "hallucination":
                insights.append(Insight(
                    description=f"{total_freq} casos de alucinación en {len(plist)} skills",
                    recommendation="Incluir verificación factual con fuentes confiables antes de responder.",
                    impact_score=min(9.0, total_freq * 0.6 + avg_conf * 5),
                ))

            elif ptype == "logic_error":
                insights.append(Insight(
                    description=f"{total_freq} errores de lógica en {len(plist)} skills",
                    recommendation="Refactorizar prompts con checklist de pasos. Añadir test de validación de salida.",
                    impact_score=min(8.5, total_freq * 0.5 + avg_conf * 5),
                ))

            elif ptype == "timeout":
                insights.append(Insight(
                    description=f"{total_freq} timeouts en {len(plist)} skills",
                    recommendation="Optimizar prompts para ser más concisos. Añadir timeout de emergencia con respuesta parcial.",
                    impact_score=min(8.0, total_freq * 0.4 + avg_conf * 4),
                ))

            elif ptype == "wrong_tool":
                insights.append(Insight(
                    description=f"{total_freq} usos incorrectos de herramientas",
                    recommendation="Restructurar tool-use prompt con ejemplos explícitos de cuándo usar cada herramienta.",
                    impact_score=min(7.5, total_freq * 0.5 + avg_conf * 3),
                ))

        # Store insights in DB
        for ins in insights:
            pattern_ids = [p["id"] for p in by_type.get(next(
                (t for t in by_type if ins.description in t), ""
            ), [])]
            self.store.add_insight(
                pattern_ids=pattern_ids,
                description=ins.description,
                recommendation=ins.recommendation,
                impact_score=ins.impact_score,
            )

        return insights

    def mine_and_insightize(self) -> tuple[list[Pattern], list[Insight]]:
        """Run both deterministic and LLM mining, then generate insights."""
        det_patterns = self.mine_deterministic()
        llm_patterns, llm_insights = self.mine_llm()
        all_insights = self.generate_insights()
        # Merge LLM insights with deterministic insights
        return det_patterns + llm_patterns, llm_insights + all_insights


__all__ = ["FailureMiner", "Pattern", "Insight"]
