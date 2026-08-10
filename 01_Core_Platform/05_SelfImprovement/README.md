# Self-Improvement Engine

Self-improving agent infrastructure for Sonora Digital Corp. Tracks task outcomes, evaluates with LLM judgment, mines failure patterns, evolves skill prompts, and runs weekly improvement cycles.

## Architecture

```
sdc_sdk.py           → env + LLM call + DB connection
experience_store.py  → SQLite: tasks, evaluations, patterns, insights, improvements
evaluator.py         → LLM-judged 5-dim scoring (correctness, efficiency, clarity, completeness)
failure_miner.py     → deterministic + LLM pattern extraction from failures
skill_evolver.py     → skill spec/test/eval/metrics lifecycle + prompt evolution
autonomous_loop.py   → weekly scheduler + reports + CLI
```

## Quick Start

```bash
# Check current status
python3 autonomous_loop.py status

# Run one improvement cycle
python3 autonomous_loop.py run

# Start weekly scheduler
python3 autonomous_loop.py schedule --interval 7
```

## Logging a Task

```python
from experience_store import ExperienceStore, TaskRecord

store = ExperienceStore()
store.log_task_simple(
    task_type="lead_scoring",
    input_text="Empresa: Aztrotech, ingresos: $50K",
    output="{'score': 85, 'tier': 'hot'}",
    status="success",
    duration_ms=1200,
    tenant_id="aztrotech",
    agent_id="cesar",
)
```

## Evaluating a Task

```python
from evaluator import Evaluator

ev = Evaluator()
result = ev.evaluate_and_store(
    task_id="task_abc123",
    task_type="lead_scoring",
    task_input="Empresa: Aztrotech",
    task_output="{'score': 85, 'tier': 'hot'}",
    status="success",
    duration_ms=1200,
)
print(f"Score: {result.score}/10")
```

## Registering a Skill

```python
from skill_evolver import SkillEvolver, EvalCase

evolver = SkillEvolver()
evolver.register_skill(
    name="lead_scoring",
    spec="# Lead Scoring Skill\n\nScores leads 1-100...\n",
    prompt="You are a lead scoring assistant...",
    tests=["assert score >= 0"],
    evals=[EvalCase(prompt="Empresa: Aztrotech", expected_behavior="Score 80+")],
)
```

## Database

SQLite at `experience.db`. Tables:

| Table | Purpose |
|-------|---------|
| `tasks` | Every task execution |
| `evaluations` | LLM-judged scores |
| `patterns` | Recurring failure/success patterns |
| `insights` | Actionable recommendations from patterns |
| `improvements` | Applied spec/test changes |

## Models

- Default: `openrouter/deepseek/deepseek-v4-flash-0731`
- API key from `~/.hermes/.env` → `OPENROUTER_API_KEY`
- Fallback evaluation (deterministic) when LLM fails

## Reports

Weekly reports saved to `reports/report_<cycle_id>.json`. Latest at `reports/latest.json`.
