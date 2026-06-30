# Sonora Digital Corp — Enterprise AI Platform

Multi-agent platform for PYMEs mexicanas: servicios digitales, contabilidad IA, automatización y más.

## Quick Start

```bash
pip install -r requirements.txt
python apps/webui/fastapp.py              # Web UI en :5174
python apps/jarvis/main.py                 # JARVIS core orchestrator
bash scripts/process-pipeline.sh status    # Pipeline status
```

## Structure

```
apps/jarvis/       → JARVIS core engine (agentes, RAG, Neo4j)
apps/webui/        → FastAPI frontend (:5174)
platforms/telegram → Telegram bot (Node.js)
infra/             → Docker, n8n, Nginx
process/           → Pipeline de procesos (SPEC→Score→TDD→ADR→Lección)
scripts/           → DevOps, backup, monitoreo
agents/            → Agent registry (MANIFEST.md)
state/             → Logs, eventos, Engram DB
products/          → Catálogo de productos digitales
```

## Tests

```bash
python -m pytest tests/unit/ -v            # 417 tests, 0 failures
python -m pytest tests/unit/ --cov=src.core # Coverage: 62%
```

## Pipeline

Every feature requires: `SPEC → Score → Gherkin → Tests-First → Code → Tests-Green → ADR → Lección`

Score gate: ≥60. CLI: `bash scripts/process-pipeline.sh <command>`

## Commands

| Comando | Qué hace |
|---------|----------|
| `bash scripts/process-pipeline.sh status` | Pipeline status |
| `bash scripts/process-pipeline.sh spec-new "Title"` | New spec |
| `bash scripts/enterprise-score.sh` | Enterprise score |
| `curl http://127.0.0.1:5174/api/enterprise-score` | Live score API |

## VPS

| IP | 149.56.46.173 |
|----|---------------|
| Web | https://sonoradigitalcorp.com |
| API | https://api.sonoradigitalcorp.com |
| Git | github.com/sonoradigitalcorp-H/Sonora-Digital-Corp |

## Constitution

- **OMEGA-PROMPT v10.0**: VDD→EDD→PDD→ODD→SDD→BDD→TDD
- **10-RULES**: Spec first, tests green, humanos deciden, todo en repo
- **JR-Lite**: 15-point checklist every spec must pass
- **TRUTH.md**: Single source of truth for all agents
