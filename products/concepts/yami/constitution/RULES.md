# 10 Absolute Rules — Sonora Digital Corp × YAMI

## 1. Spec First, Always

No code without an approved `spec.md`. No exceptions. The spec must include Gherkin scenarios.

## 2. Tests Must Be Green

All tests must pass before merge. CI enforces this. If tests fail, the PR is blocked. No force-push to skip.

## 3. Humans Decide

Every spec, ADR, and PR requires human approval. The agent proposes; the human disposes.

## 4. Everything in the Repo

Code, specs, ADRs, decisions, memory — all in `SonoraDigitalCorp-Yami/`. If it's not committed, it's not real.

## 5. PR Required + 1 Approval

Every change to `main` goes through a PR. Branch protection enforces at least 1 approval. That includes both of us.

## 6. OpenCode Always

The sole agent is OpenCode. No Copilot, no Claude Code, no Codex as primary. Each chooses their own LLM via OpenRouter.

## 7. Stack is Fixed

Python 3.10+, pytest, GitHub Actions, OpenRouter. No tech change without an approved ADR.

## 8. Continuous Learning

Every sprint, write lessons to `memory/lecciones.json`. The agent reads memory before proposing specs.

## 9. Value First

Every feature must tie to a business metric (revenue, retention, CAC, LTV). If it doesn't create value, it doesn't ship.

## 10. One Brain

One repo, one truth, one constitution, many products. Products share infrastructure via MCP, not duplication.
