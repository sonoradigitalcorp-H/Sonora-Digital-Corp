# Truth Hierarchy — Sonora Digital Corp × YAMI

> "La IA explica, NO decide."

## Hierarchy (highest → lowest authority)

```
CLIENT REQUEST
     │
     ▼
APPROVED SPEC (spec.md)
     │
     ▼
ARCHITECTURE DECISION RECORD (ADR)
     │
     ▼
TASK (tasks.md)
     │
     ▼
TESTS (feature files + pytest)
     │
     ▼
IMPLEMENTATION (code)
     │
     ▼
DOCUMENTATION (docs/)
     │
     ▼
MEMORY (memory/)
     │
     ▼
ASSUMPTIONS (anything not written above)
```

## Rules

1. **Write before code** — Spec first, always. No implementation without an approved spec.
2. **Tests are law** — Code is not complete until all tests pass.
3. **Humans close the loop** — Every spec, ADR, and PR requires human approval.
4. **Everything in the repo** — If it's not in this repo, it doesn't exist. No ephemeral chat as source of truth.
5. **Memory is not truth** — `memory/` is a learning aid, never override spec/ADR/test with memory.
6. **When in doubt, go up** — If something contradicts, the higher item in the hierarchy wins.
7. **ADR before tech change** — Any significant tech decision requires an approved ADR before implementation.

## Derived from

- OMEGA PROMPT v10.0 (consultar en sonora-digital-corp para referencia completa)
- Gentleman Programmer methodology
- SDD (Spec-Driven Development)
