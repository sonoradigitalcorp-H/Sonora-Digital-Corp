"""Skill Evolver — manage skill specs, tests, evals, and metrics.

For each skill in 01_Core_Platform/05_SelfImprovement/skills/<skill_name>/:
  spec.md      — deterministic specification (prompt, behavior, edge cases)
  tests/       — pytest test files (deterministic behavior checks)
  evals/       — LLM evaluation cases (prompt, expected_behavior, rubric)
  metrics.json — runtime metrics (score, failure_types, last_evaluated, version)
  prompt.txt   — the current prompt/skill definition (evolvable)

Evolution workflow:
  1. Run tests → if any fail, mine the failure
  2. Run evals → score output
  3. If score dropped, use failure_miner to extract insight
  4. Apply insight to spec.md / prompt.txt → bump version
  5. Record improvement in experience store
"""

import json
import os
import subprocess
import time
import hashlib
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

from sdc_sdk import SKILLS_DIR, call_llm, log_action
from experience_store import ExperienceStore

EVAL_PROMPT = """Evalúa este caso de prueba para el skill '{skill_name}'.

ESPECIFICACIÓN DEL SKILL:
{spec}

CASO DE EVALUACIÓN:
  prompt: {eval_prompt}
  expected: {eval_expected}
  rubric: {eval_rubric}

SALIDA DEL SKILL:
{actual_output}

Califica 1-10 en cada dimensión y devuelve JSON:
{
  "correctness": <0-10>,
  "relevance": <0-10>,
  "clarity": <0-10>,
  "overall": <0-10>,
  "notes": "<2-3 frases>"
}"""


@dataclass
class EvalCase:
    prompt: str
    expected_behavior: str
    rubric: str = "Output should be correct, relevant, and complete."
    id: str = ""


@dataclass
class SkillMetrics:
    name: str
    version: float = 1.0
    last_evaluated: float = 0.0
    avg_score: float = 0.0
    success_count: int = 0
    failure_count: int = 0
    failure_types: dict = field(default_factory=dict)
    best_prompt_hash: str = ""
    improvement_history: list = field(default_factory=list)


class SkillEvolver:
    """Manage skill lifecycle, testing, evaluation, and evolution."""

    def __init__(self, skills_dir: Optional[Path] = None, store: Optional[ExperienceStore] = None, model: Optional[str] = None):
        self.skills_dir = skills_dir or SKILLS_DIR
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self.store = store or ExperienceStore()
        self.model = model

    def register_skill(self, name: str, spec: str, prompt: str, tests: list[str] = None, evals: list[EvalCase] = None) -> None:
        """Register a new skill with spec, tests, and evals."""
        skill_dir = self.skills_dir / name
        skill_dir.mkdir(parents=True, exist_ok=True)

        (skill_dir / "spec.md").write_text(spec, encoding="utf-8")
        (skill_dir / "prompt.txt").write_text(prompt, encoding="utf-8")

        # tests
        tests_dir = skill_dir / "tests"
        tests_dir.mkdir(exist_ok=True)
        for i, test_code in enumerate(tests or []):
            (tests_dir / f"test_{i+1}.py").write_text(test_code, encoding="utf-8")

        # evals
        evals_dir = skill_dir / "evals"
        evals_dir.mkdir(exist_ok=True)
        for i, ev in enumerate(evals or []):
            ev_data = {
                "id": ev.id or f"eval_{i+1}",
                "prompt": ev.prompt,
                "expected_behavior": ev.expected_behavior,
                "rubric": ev.rubric,
            }
            (evals_dir / f"eval_{i+1}.json").write_text(
                json.dumps(ev_data, ensure_ascii=False, indent=2), encoding="utf-8"
            )

        # metrics
        metrics = SkillMetrics(name=name)
        (skill_dir / "metrics.json").write_text(
            json.dumps(metrics.__dict__, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )

        log_action("skill_registered", metadata={"skill": name})

    def get_skill_names(self) -> list[str]:
        """List all registered skills."""
        if not self.skills_dir.exists():
            return []
        return [d.name for d in self.skills_dir.iterdir() if d.is_dir()]

    def load_metrics(self, skill_name: str) -> Optional[SkillMetrics]:
        metrics_path = self.skills_dir / skill_name / "metrics.json"
        if not metrics_path.exists():
            return None
        data = json.loads(metrics_path.read_text(encoding="utf-8"))
        data["failure_types"] = data.get("failure_types", {})
        data["improvement_history"] = data.get("improvement_history", [])
        return SkillMetrics(**data)

    def save_metrics(self, metrics: SkillMetrics) -> None:
        metrics_path = self.skills_dir / metrics.name / "metrics.json"
        data = {
            "name": metrics.name,
            "version": metrics.version,
            "last_evaluated": metrics.last_evaluated,
            "avg_score": metrics.avg_score,
            "success_count": metrics.success_count,
            "failure_count": metrics.failure_count,
            "failure_types": metrics.failure_types,
            "best_prompt_hash": metrics.best_prompt_hash,
            "improvement_history": metrics.improvement_history,
        }
        metrics_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )

    def run_tests(self, skill_name: str) -> dict:
        """Run pytest on skill's tests directory. Returns results."""
        skill_dir = self.skills_dir / skill_name
        tests_dir = skill_dir / "tests"
        if not tests_dir.exists():
            return {"passed": True, "total": 0, "failures": []}

        result = subprocess.run(
            ["python3", "-m", "pytest", str(tests_dir), "-v", "--tb=short", "-x"],
            capture_output=True, text=True, timeout=60,
            cwd=str(self.skills_dir),
        )

        passed = result.returncode == 0
        failures = []
        for line in result.stdout.split("\n"):
            if "FAILED" in line:
                failures.append(line.strip())

        return {
            "passed": passed,
            "total": result.stdout.count(" PASSED"),
            "failures": failures,
            "stdout": result.stdout[-500:] if result.stdout else "",
            "stderr": result.stderr[-500:] if result.stderr else "",
        }

    def run_evals(self, skill_name: str, skill_executor) -> list[dict]:
        """Run LLM evaluation cases for a skill.

        Args:
            skill_name: name of the skill directory
            skill_executor: callable that takes (prompt, eval_prompt) -> output string
        """
        skill_dir = self.skills_dir / skill_name
        evals_dir = skill_dir / "evals"
        if not evals_dir.exists():
            return []

        results = []
        for eval_file in sorted(evals_dir.glob("eval_*.json")):
            ev_data = json.loads(eval_file.read_text(encoding="utf-8"))
            eval_id = ev_data.get("id", eval_file.stem)
            eval_prompt = ev_data["prompt"]
            expected = ev_data["expected_behavior"]
            rubric = ev_data.get("rubric", "Output should be correct and relevant.")

            # Execute the skill
            try:
                actual_output = skill_executor(skill_name, eval_prompt)
            except Exception as e:
                actual_output = f"ERROR: {e}"

            # Evaluate with LLM
            spec_path = skill_dir / "spec.md"
            spec = spec_path.read_text(encoding="utf-8")[:2000] if spec_path.exists() else ""

            eval_result = call_llm(
                prompt=EVAL_PROMPT.format(
                    skill_name=skill_name,
                    spec=spec,
                    eval_prompt=eval_prompt[:1000],
                    eval_expected=expected[:500],
                    eval_rubric=rubric[:300],
                    actual_output=actual_output[:3000],
                ),
                system="Eres un evaluador de IA imparcial. Devuelve JSON válido.",
                model=self.model,
                max_tokens=1024,
                temperature=0.2,
            )

            try:
                parsed = json.loads(eval_result.strip().strip("```"))
            except json.JSONDecodeError:
                parsed = {"overall": 5.0, "correctness": 5, "relevance": 5, "clarity": 5, "notes": "parse error"}

            result = {
                "skill": skill_name,
                "eval_id": eval_id,
                "score": parsed.get("overall", 5.0),
                "correctness": parsed.get("correctness", 5),
                "relevance": parsed.get("relevance", 5),
                "clarity": parsed.get("clarity", 5),
                "notes": parsed.get("notes", ""),
                "output": actual_output[:500],
                "timestamp": time.time(),
            }
            results.append(result)

            # Log to experience store
            self.store.log_task_simple(
                task_type=f"eval:{skill_name}",
                input_text=eval_prompt,
                output=actual_output,
                status="success" if result["score"] >= 7 else "failure",
                tenant_id="sdc",
                agent_id=skill_name,
            )

        return results

    def evolve_prompt(self, skill_name: str, current_score: float, min_score: float = 7.0) -> bool:
        """If score is below threshold, evolve the skill prompt based on failure patterns."""
        if current_score >= min_score:
            return False

        skill_dir = self.skills_dir / skill_name
        prompt_path = skill_dir / "prompt.txt"
        spec_path = skill_dir / "spec.md"
        metrics = self.load_metrics(skill_name)

        if not prompt_path.exists():
            return False

        current_prompt = prompt_path.read_text(encoding="utf-8")

        # Mine recent failures for this skill
        failures = self.store.get_failures(limit=50)
        skill_failures = [f for f in failures if f.get("agent_id") == skill_name]

        if not skill_failures:
            return False

        failure_summary = json.dumps(skill_failures, indent=2, default=str)

        evolve_prompt = f"""El skill '{skill_name}' tiene un score promedio de {current_score:.1f}/10.
Analiza las fallas y mejora el prompt. Mantén la esencia pero corrige las deficiencias.

PROMPT ACTUAL:
{current_prompt}

FALLAS RECIENTES:
{failure_summary[:3000]}

Devuelve el prompt mejorado como texto plano (sin markdown)."""

        improved_prompt = call_llm(
            prompt=evolve_prompt,
            system="Eres un ingeniero de prompts senior. Mejora prompts manteniendo su esencia.",
            model=self.model,
            max_tokens=2048,
            temperature=0.5,
        )

        if improved_prompt and len(improved_prompt) > 50:
            # Save evolution
            prompt_hash = hashlib.sha256(improved_prompt.encode()).hexdigest()[:16]
            if metrics and metrics.best_prompt_hash == prompt_hash:
                # Already evolved to this version
                return False

            prompt_path.write_text(improved_prompt, encoding="utf-8")

            # Track in metrics
            if metrics:
                metrics.version += 0.1
                metrics.best_prompt_hash = prompt_hash
                metrics.improvement_history.append({
                    "version": round(metrics.version, 1),
                    "reason": f"avg_score {current_score:.1f} < {min_score}",
                    "timestamp": time.time(),
                })
                self.save_metrics(metrics)

            # Log to experience store
            self.store.log_improvement(
                skill_name=skill_name,
                spec_diff=f"Evolved prompt from score {current_score:.1f}",
                parent_run_id=f"skill:{skill_name}",
            )

            log_action("prompt_evolved", metadata={"skill": skill_name, "old_score": current_score})
            return True

        return False

    def audit_and_evolve_all(self) -> dict:
        """Run full audit on all skills: tests → evals → evolve."""
        skills = self.get_skill_names()
        results = {"skills": [], "improvements": []}

        for skill_name in skills:
            test_result = self.run_tests(skill_name)
            eval_results = self.run_evals(skill_name, lambda s, p: f"[test] {p}")  # stub executor

            if eval_results:
                avg_score = sum(r["score"] for r in eval_results) / len(eval_results)
            else:
                avg_score = test_result["passed"] * 10.0

            metrics = self.load_metrics(skill_name)
            if metrics:
                metrics.last_evaluated = time.time()
                metrics.avg_score = avg_score
                if avg_score >= 7:
                    metrics.success_count += 1
                else:
                    metrics.failure_count += 1
                self.save_metrics(metrics)

            evolved = self.evolve_prompt(skill_name, avg_score) if avg_score < 7.0 else False

            results["skills"].append({
                "name": skill_name,
                "tests_passed": test_result["passed"],
                "eval_count": len(eval_results),
                "avg_score": round(avg_score, 2),
                "evolved": evolved,
            })
            if evolved:
                results["improvements"].append(f"skill:{skill_name}:evolved_prompt")

        return results


__all__ = ["SkillEvolver", "SkillMetrics", "EvalCase"]
