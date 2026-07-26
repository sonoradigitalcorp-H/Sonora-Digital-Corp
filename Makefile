# Sonora Digital Corp — Makefile
# Commands for local development, testing, and evaluation

.PHONY: help test test-all test-v lint lint-fix eval eval-structural eval-promptfoo clean

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ─── Tests ───────────────────────────────────────────────────────────────────

test:  ## Run unit tests (known stable subset)
	PYTHONPATH=. python3 -m pytest tests/unit/ -q --tb=short

test-all:  ## Run all tests (unit + bdd + integration)
	PYTHONPATH=. python3 -m pytest tests/unit/ tests/gherkin/ tests/integration/ core/tests/ -q --tb=short

test-v:  ## Run all tests verbose
	PYTHONPATH=. python3 -m pytest tests/unit/ tests/gherkin/ tests/integration/ core/tests/ -v --tb=short

test-integration:  ## Run integration tests only (real services)
	PYTHONPATH=. python3 -m pytest tests/integration/ -v --tb=short

# ─── SDD ───────────────────────────────────────────────────────────────────

sdd-test:  ## Run SDD BDD + structural tests
	sdd test

sdd-eval:  ## Run SDD evals (structural only)
	sdd eval

sdd-init:  ## Initialize SDD framework structure
	sdd init

# ─── Evals ───────────────────────────────────────────────────────────────────

eval: eval-structural eval-promptfoo  ## Run all evaluations

eval-structural:  ## Run structural evals (agent/cap/sdd/skill/event)
	PYTHONPATH=. python3 -m pytest evals/structural/ -v --tb=short

eval-promptfoo:  ## Run SDD promptfoo LLM evals
	cd evals/promptfoo && promptfoo eval && cd ../..

eval-dashboard:  ## Generate eval dashboard HTML
	PYTHONPATH=. python3 evals/generate-dashboard.py

# ─── Enterprise Score ────────────────────────────────────────────────────────

score:  ## Run observer and show scorecard
	bash scripts/observer-run.sh

# ─── Constitution ────────────────────────────────────────────────────────────

constitution-gate:  ## Run constitution gate on active plan
	python3 scripts/constitution-gate.py --plan process/active/PLAN.yaml

# ─── Clean ───────────────────────────────────────────────────────────────────

clean:  ## Clean cache and temp files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf .mypy_cache .coverage htmlcov 2>/dev/null || true
