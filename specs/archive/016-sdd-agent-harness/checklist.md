# Implementation Checklist: SDD Agent Harness

**Spec**: 016-sdd-agent-harness/spec.md
**Created**: 2026-06-10

---

## Registry Setup

- [ ] CHK001 registry-create — Create config/registry.json with indexed skills
- [ ] CHK002 registry-validate — Validate registry against existing agents
- [ ] CHK003 registry-sync — Sync registry with live skill inventory

## Engram Implementation

- [ ] CHK004 engram-create — Implement SQLite + FTS5 engine in src/core/engram.py
- [ ] CHK005 engram-store — Test storing/retrieving technical lessons
- [ ] CHK006 engram-query — Validate semantic search functionality

## Harness Pipeline

- [ ] CHK007 harness-create — Create src/core/harness.py with phase orchestration
- [ ] CHK008 harness-integrate — Integrate with existing AgentOrchestrator
- [ ] CHK009 harness-validate — Test full pipeline execution

## Quality Gates

- [ ] CHK010 verify-enhanced — Update verify.py with SDD checks
- [ ] CHK011 tdd-gate — Implement pre-commit TDD validation
- [ ] CHK012 ci-integration — Add harness checks to GitHub Actions

## Documentation

- [ ] CHK013 docs-update — Update INVENTARIO-FINAL.md with harness metrics
- [ ] CHK014 docs-spec — Create README.md for harness module
- [ ] CHK015 docs-example — Add usage examples to spec.md

---

## Notes

- Check items off as completed: `[x]`
- 15 items total