# AGENTS.md — Mystic + Noel

## Mystic

- **Role**: Co-founder, infra, automation, AI systems
- **Preferred LLM**: Qwen 2.5 / DeepSeek V3 via OpenRouter
- **Stack**: Python, GitHub Actions, Neo4j, Qdrant, VPS
- **Focus**: Specs, ADRs, analizador, infra, CI/CD, LLM pipelines

## Noel

- **Role**: Co-founder, product, UX, deploy
- **Preferred LLM**: Claude 3.5 Sonnet / Codex via OpenRouter
- **Stack**: Python, Vercel, Whisper, productos YAMI
- **Focus**: Product specs, landings, user-facing features, frontend

## System

- **Agent**: OpenCode (always)
- **LLM Provider**: OpenRouter (each chooses own)
- **CI/CD**: GitHub Actions
- **Tests**: pytest
- **Language**: Python 3.10+
- **Memory**: `memory/lecciones.json` + `memory/patrones.md`

## Protocol

1. Read `constitution/TRUTH.md` before any work
2. Read `constitution/RULES.md` before any PR
3. Read `memory/lecciones.json` before spec'ing
4. Write spec before code
5. Write tests before implementation
6. Open PR, wait for approval
7. Write lessons after every sprint
