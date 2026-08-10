"""Self-Improvement Engine — core modules and CLI.

Modules:
  sdc_sdk.py          — SDK utilities (env, LLM, DB, logging)
  experience_store.py — SQLite experience log (tasks, evaluations, patterns, insights)
  evaluator.py        — LLM-judged scoring of task outputs
  failure_miner.py    — deterministic + LLM pattern mining from failures
  skill_evolver.py    — skill spec/test/eval/metrics lifecycle
  autonomous_loop.py  — weekly auto-improvement scheduler + CLI

CLI:
  python3 autonomous_loop.py run       — single improvement cycle
  python3 autonomous_loop.py status    — show current stats
  python3 autonomous_loop.py schedule  — run weekly (cron mode)

Usage from OpenCode:
  The engine auto-logs tasks via ExperienceStore.log_task().
  Evaluator scores them post-hoc.
  FailureMiner extracts patterns weekly.
  SkillEvolver evolves prompts when scores drop.
"""

import sys
from pathlib import Path

# Ensure imports work when run from any cwd
sys.path.insert(0, str(Path(__file__).resolve().parent))
