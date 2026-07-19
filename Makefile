# Sonora Digital Corp — Makefile
# Commands for local development, testing, and evaluation

.PHONY: help test test-all lint lint-fix eval eval-structural eval-promptfoo clean

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ─── Tests ───────────────────────────────────────────────────────────────────

test:  ## Run all unit tests
	PYTHONPATH=. python3 -m pytest tests/ -q --tb=short

test-all:  ## Run all tests (unit + evals + memory)
	PYTHONPATH=. python3 -m pytest tests/ evals/ memory/tests/ -q --tb=short

test-v:  ## Run all tests with verbose output
	PYTHONPATH=. python3 -m pytest tests/ evals/ memory/tests/ -v --tb=short

# ─── Lint ────────────────────────────────────────────────────────────────────

lint:  ## Run ruff linter
	ruff check apps/ memory/ metrics/ scripts/

lint-fix:  ## Auto-fix lint issues
	ruff check --fix apps/ memory/ metrics/ scripts/

# ─── Evals ───────────────────────────────────────────────────────────────────

eval: eval-structural eval-promptfoo  ## Run all evaluations

eval-structural:  ## Run structural evals (agent/cap/sdd/skill/event)
	PYTHONPATH=. python3 -m pytest evals/test_evals.py -v --tb=short

eval-promptfoo:  ## Run promptfoo LLM evals
	cd promptfoo && promptfoo eval && cd ..

eval-dashboard:  ## Generate eval dashboard HTML
	PYTHONPATH=. python3 evals/generate-dashboard.py

# ─── Enterprise Score ────────────────────────────────────────────────────────

score:  ## Calculate enterprise score
	python3 metrics/enterprise_score.py

score-json:  ## Calculate enterprise score (JSON)
	python3 metrics/enterprise_score.py --json

# ─── Constitution ────────────────────────────────────────────────────────────

constitution-gate:  ## Run constitution gate on active plan
	python3 scripts/constitution-gate.py --plan process/active/PLAN.yaml

# ─── Clean ───────────────────────────────────────────────────────────────────

clean:  ## Clean cache and temp files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf .mypy_cache .coverage htmlcov 2>/dev/null || true
