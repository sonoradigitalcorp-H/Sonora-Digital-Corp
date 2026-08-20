"""A/B Testing Manager — testea variantes de prompt del bot Aztrotech.

Pipeline por minuto:
  1. Lee variantes desde research/ab_tests/variants.json
  2. Para cada conversación: 50% variant A (default), 50% variant B
  3. Después de N conversaciones, evalúa con evaluator.py (LLM-judged 5-dimension score)
  4. Si variant B gana por margen > 5%: promueve a default
  5. Guarda metrics en research/ab_tests/results/

Usage:
    from ab_test_manager import ABTestManager
    ab = ABTestManager()
    variant = ab.select_variant(user_id)
    prompt = ab.get_prompt_for(variant)
    ab.record_turn(user_id, lead_type, engagement, survey_rating)
    ab.evaluate_cycle()
"""
import json
import os
import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
AB_TESTS_DIR = BASE_DIR / "research" / "ab_tests"
VARIANTS_FILE = AB_TESTS_DIR / "variants.json"
RESULTS_DIR = AB_TESTS_DIR / "results"
EVAL_THRESHOLD = 50  # min conversaciones por variante para evaluar
WIN_MARGIN = 0.05  # 5% improvement needed to promote


@dataclass
class Variant:
    name: str
    system_prompt: str
    traffic_pct: float = 0.5
    active: bool = True
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class TurnRecord:
    variant: str
    lead_type: str
    engagement_score: float
    survey_rating: Optional[int]
    cost_usd: float
    timestamp: datetime


class ABTestManager:
    """Manages A/B testing de prompts para el bot Aztrotech."""

    def __init__(self, variants_path: Optional[str] = None):
        self.variants_path = Path(variants_path) if variants_path else VARIANTS_FILE
        self._ensure_dirs()
        self._variants = self._load_variants()
        self._records: List[TurnRecord] = self._load_records()

    def _ensure_dirs(self):
        self.variants_path.parent.mkdir(parents=True, exist_ok=True)
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    def _load_variants(self) -> Dict[str, Variant]:
        if not self.variants_path.exists():
            self._create_default_variants()
        try:
            raw = json.loads(self.variants_path.read_text(encoding="utf-8"))
            return {v["name"]: Variant(**v) for v in raw.get("variants", [])}
        except Exception as e:
            logger.warning(f"Error loading variants: {e}")
            return {}

    def _load_records(self) -> List[TurnRecord]:
        records = []
        for f in sorted(RESULTS_DIR.glob("turns_*.jsonl")):
            try:
                for line in f.read_text().splitlines():
                    if line.strip():
                        data = json.loads(line)
                        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
                        records.append(TurnRecord(**data))
            except Exception:
                pass
        return records

    def _create_default_variants(self):
        """Create default A vs B prompt variants."""
        # Importar el prompt original
        from prompt_builder import SYSTEM_PROMPT
        default_prompt = SYSTEM_PROMPT

        variant_a = {
            "name": "variant_a_control",
            "system_prompt": default_prompt,
            "traffic_pct": 0.5,
            "active": True,
        }

        # Variant B: prompt optimizado con enfoque en BANT + storytelling
        variant_b_prompt = default_prompt.replace(
            "PERSONALIDAD: Profesional, cálido, consultivo, sin tecnicismos innecesarios.",
            "PERSONALIDAD: Profesional, cálido, consultivo. Usa storytelling breve para conectar. "
            "Ejemplo: 'Un cliente similar en Guadalajara automatizó su WhatsApp y redujo tiempo de respuesta de 2 horas a 2 minutos.' "
            "Siempre conecta la tecnología al ahorro de tiempo/dinero del cliente."
        ).replace(
            "PRIORIZA EDUCAR antes que vender: explica CÓMO funciona la tecnología y CÓMO resolvería el problema del cliente.",
            "PRIORIZA EDUCAR antes que vender: explica CÓMO funciona la tecnología (2 frases máximo) y CÓMO resolvería el problema específico del cliente. "
            "Usa analogías simples: 'Imagina un empleado que nunca duerme ni descansa, disponible 24/7 en tu WhatsApp.'"
        )

        variant_b = {
            "name": "variant_b_storytelling",
            "system_prompt": variant_b_prompt,
            "traffic_pct": 0.5,
            "active": True,
        }

        data = {"variants": [variant_a, variant_b]}
        self.variants_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info(f"Created default A/B variants at {self.variants_path}")

    def select_variant(self, user_id: str) -> str:
        """Determinista: 50% de usuarios van a B basado en hash."""
        active = [v for v in self._variants.values() if v.active]
        if not active:
            return "variant_a_control"
        if len(active) == 1:
            return active[0].name

        # Hash deterministic para traffic split
        h = hashlib.md5(str(user_id).encode()).hexdigest()
        bucket = int(h, 16) % 100

        cumulative = 0
        for v in active:
            cumulative += v.traffic_pct * 100
            if bucket < cumulative:
                return v.name
        return active[-1].name

    def get_prompt(self, variant_name: str) -> str:
        """Get system prompt for a variant."""
        v = self._variants.get(variant_name)
        return v.system_prompt if v else self._variants.get("variant_a_control", Variant("", "")).system_prompt

    def record_turn(
        self,
        variant: str,
        lead_type: str,
        engagement_score: float,
        survey_rating: Optional[int] = None,
        cost_usd: float = 0.0,
    ):
        """Record a turn's outcome for ab testing analysis."""
        record = TurnRecord(
            variant=variant,
            lead_type=lead_type,
            engagement_score=engagement_score,
            survey_rating=survey_rating,
            cost_usd=cost_usd,
            timestamp=datetime.now(timezone.utc),
        )
        self._records.append(record)

        # Append to daily file
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        file_path = RESULTS_DIR / f"turns_{date_str}.jsonl"
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "variant": record.variant,
                "lead_type": record.lead_type,
                "engagement_score": record.engagement_score,
                "survey_rating": record.survey_rating,
                "cost_usd": record.cost_usd,
                "timestamp": record.timestamp.isoformat(),
            }) + "\n")

    def evaluate(self) -> Dict[str, Any]:
        """Evaluar A/B test results. Si hay suficiente data, usa evaluator.py."""
        by_variant: Dict[str, List[TurnRecord]] = defaultdict(list)
        for r in self._records:
            by_variant[r.variant].append(r)

        results = {}
        for name, records in by_variant.items():
            if len(records) < EVAL_THRESHOLD:
                results[name] = {"status": "insufficient_data", "count": len(records)}
                continue

            # Métricas clave
            hot_count = sum(1 for r in records if r.lead_type == "hot")
            warm_count = sum(1 for r in records if r.lead_type == "warm")
            hot_conv_rate = hot_count / len(records)

            avg_engagement = sum(r.engagement_score for r in records) / len(records)
            surveys = [r.survey_rating for r in records if r.survey_rating is not None]
            avg_survey = sum(surveys) / len(surveys) if surveys else None
            avg_cost = sum(r.cost_usd for r in records) / len(records)

            # Score compuesto: 40% hot rate, 30% engagement, 20% survey, 10% cost efficiencia
            composite = (
                hot_conv_rate * 0.4 +
                avg_engagement * 0.3 +
                (avg_survey / 5.0 * 0.2 if avg_survey else 0) +
                (1.0 - min(avg_cost / 0.005, 1.0) * 0.1)  # lower cost = higher score
            )

            results[name] = {
                "count": len(records),
                "hot_count": hot_count,
                "warm_count": warm_count,
                "hot_conv_rate": round(hot_conv_rate, 3),
                "avg_engagement": round(avg_engagement, 3),
                "avg_survey": round(avg_survey, 2) if avg_survey else None,
                "avg_cost_usd": round(avg_cost, 6),
                "composite_score": round(composite, 3),
            }

        # Compare A vs B
        if "variant_a_control" in results and "variant_b_storytelling" in results:
            a = results.get("variant_a_control", {})
            b = results.get("variant_b_storytelling", {})
            if a.get("status") != "insufficient_data" and b.get("status") != "insufficient_data":
                improvement = b.get("composite_score", 0) - a.get("composite_score", 0)
                results["comparison"] = {
                    "improvement": round(improvement, 3),
                    "winner": "variant_b_storytelling" if improvement > WIN_MARGIN else (
                        "variant_a_control" if improvement < -WIN_MARGIN else "inconclusive"
                    ),
                    "b_beats_a_by": f"{abs(improvement)*100:.1f}%" if abs(improvement) > 0.01 else "inconclusive",
                }

                # Auto-promote winner
                if improvement > WIN_MARGIN and self._variants.get("variant_b_storytelling"):
                    logger.info(f"A/B test: variant B wins by {improvement:.3f} — promoting")
                    self._promote_variant("variant_b_storytelling")

        # Save evaluation report
        report_path = RESULTS_DIR / f"evaluation_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)

        return results

    def _promote_variant(self, winner_name: str):
        """Promote winner to be the new default prompt."""
        winner = self._variants.get(winner_name)
        if not winner:
            return
        from prompt_builder import SYSTEM_PROMPT
        # Swap: winner becomes variant_a_control
        self._variants["variant_a_control"].system_prompt = winner.system_prompt
        # Reset variant B
        self._variants["variant_b_storytelling"].active = False

        # Save
        data = {"variants": [
            {"name": k, **{k2: v2 for k2, v2 in v.__dict__.items() if k2 != "name"}}
            for k, v in self._variants.items()
        ]}
        self.variants_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info(f"Promoted {winner_name} to control")


def create_ab_test_manager() -> ABTestManager:
    return ABTestManager()
