---
id: ADR-20260721-SDD-FRAMEWORK
title: SDD Framework — Canonical Specs, ADRs, Evals, and BDD
status: accepted
date: 2026-07-21
---

# SDD Framework Implementation

## Context
The project already uses Spec-Driven Development (SDD) via `process/` workspace and `.specify/` Spec Kit, but lacks:
- A canonical `specs/` directory serving as the single source of truth for business capabilities
- A dedicated `adrs/` directory indexed for decision archaeology
- Executable BDD tests (Gherkin + pytest-bdd step definitions)
- A structured `evals/` pipeline for LLM and structural evaluations
- A CLI tool (`sdd`) for common SDD workflows

## Decision
Create a unified SDD framework at repo root with these conventions:

1. **specs/** — Canonical capability specs, one subdirectory per capability, each with `spec.md`, `tasks.md`, `plan.md`, `adr.md`, and `gherkin/`.
2. **adrs/** — ADRs copied from `process/active/` (plus `process/completed/*/ADR.md`) with an index.
3. **tests/gherkin/** + **tests/steps/** — BDD tests using pytest-bdd, with step definitions that delegate to fixtures/mocks.
4. **evals/** — LLM evals (Promptfoo, local + remote) + structural integrity tests.
5. **tools/sdd/** — CLI package with `sdd init`, `sdd test`, `sdd eval`, `sdd spec-new`.
6. **skills/speckit/** — OpenClaw skills mirroring `/speckit.*` commands.

The `process/` directory remains the active sprint workspace. When a spec is completed, it's copied from `process/active/` to `specs/capabilities/<id>/` and indexed in `specs/index.yaml`.

## Consequences
- Developers and AI agents have one canonical location for specs.
- Gherkin tests become executable with `pytest tests/gherkin/`.
- Evals run with `sdd eval` or `promptfoo eval -c evals/promptfoo/promptfooconfig.yaml`.
- All future capabilities MUST include `spec.md` and `gherkin/` at minimum.
- The `sdd` CLI reduces typing and standardizes workflows.

## Options Considered
- Keep everything in `process/` — rejected because it mixes active sprint work with canonical specs.
- Use separate repos for specs — rejected because monorepo co-location is simpler.
