# HAS-007 — Hermes Architecture Standard: Pipeline Evolution

**Status:** Draft v1
**Domain:** process
**Updated:** 2026-07-08
**Depends on:** HAS-000, HAS-001
**Replaces:** `process/CONDUCT.md` pipeline (VDD→TDD)

---

## 1. Purpose

Define the new pipeline that replaces VDD→EDD→PDD→ODD→SDD→BDD→TDD. The pipeline is now **Mission → Evolution** with 10 stages and tiered gates.

---

## 2. Pipeline Stages

```
 1. MISSION       ──  Purpose, north star, business goal
       │
 2. CONSTITUTION  ──  Validate against all constitution rules
       │
 3. RESEARCH      ──  Knowledge: papers, benchmarks, competitors, experiments
       │
 4. ARCHITECTURE  ──  ADR, patterns, contracts, capability mapping
       │
 5. SIMULATION    ──  Risk analysis, cost estimation, security review
       │
 6. SPECIFICATION ──  SDD with Gherkin + FRs + Score
       │
 7. IMPLEMENTATION──  Code + tests (BDD + TDD)
       │
 8. VERIFICATION  ──  All gates: constitution gates + tests + coverage + lint
       │
 9. OBSERVABILITY ──  Deploy + monitor + trace + alert
       │
10. EVOLUTION     ──  Score → ADR → Refactor → Update prompts → Close session
```

---

## 3. Tier System

| Tier | Scope | Pipeline Stages | Gates |
|---|---|---|---|
| 0 | Typo, config, comment | 7 → 8 | Tests green |
| 1 | Quick fix, minor bug | 3 → 7 → 8 → 9 | Constitution + Tests |
| 2 | Feature, improvement | 4 → 6 → 7 → 8 → 9 | Full constitution + Tests + Score ≥60 |
| 3 | Capability, platform | 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 | All gates + ADR + Score ≥75 |

---

## 4. Gate Definitions

### Gate 0: Sync Gate
```bash
scripts/git-sync.sh --status
```
- PASS: repo in sync, no stuck rebase/merge
- FAIL: divergence or stuck operation — fix first

### Gate 1: Constitution Gate (replaces verify-gate)
```bash
python3 scripts/constitution-gate.py --plan process/active/PLAN.yaml
```
- 6 sub-gates: Policy → Security → Cost → Compliance → Quality → Knowledge
- All must PASS

### Gate 2: Tests Gate
```bash
python3 -m pytest tests/ -q --tb=short
```
- PASS: all tests green (Tier 0-1)
- PASS: ≥90% new code coverage (Tier 2+)

### Gate 3: Lint Gate
```bash
ruff check --quiet
```
- PASS: 0 errors

### Gate 4: Score Gate
```bash
python3 scripts/score-gate.py --spec process/active/SPEC-*.md
```
- PASS: Score ≥60 (Tier 2), ≥75 (Tier 3)

### Gate 5: ADR Gate (Tier 3 only)
```bash
test -f process/active/ADR-*.md
```
- PASS: ADR filed for architecture decisions

---

## 5. Migration: Old Pipeline → New Pipeline

| Old Stage | New Stage | Status |
|---|---|---|
| VDD (Vision) | 1. Mission | Renamed — broader scope |
| EDD (Exploration) | 3. Research | Renamed + formalized |
| PDD (Planning) | 4. Architecture | Renamed — includes planning |
| ODD (Design) | Merged into 4+5 | Architecture + Simulation |
| SDD (Spec) | 6. Specification | Same — uses existing templates |
| BDD (Build) | 7. Implementation | Same |
| TDD (Test) | 8. Verification | Expanded with all gates |
| (missing) | 2. Constitution | NEW — was implicit |
| (missing) | 5. Simulation | NEW — formal risk/cost/security |
| (missing) | 9. Observability | NEW — post-deploy |
| Close Session | 10. Evolution | Renamed — includes learning |

---

## 6. File Organization

```
process/
├── CONDUCT.md              # Updated to HAS-007
├── templates/              # Updated templates for new stages
│   ├── MISSION.md          # Template for Mission stage
│   ├── RESEARCH.md         # Template for Research stage
│   ├── ARCHITECTURE.md     # Template for Architecture stage
│   ├── SIMULATION.md       # Template for Simulation stage
│   ├── SPEC.md             # Existing — updated
│   ├── ADR.md              # Existing
│   ├── SCORE.md            # Existing
│   ├── LECCION.md          # Existing
│   └── GHERKIN.md          # Existing
├── active/                 # Active specs (same)
├── completed/              # Completed specs (same)
└── has/                    # HAS specifications
```

---

## 7. Success Criteria

- [ ] `process/CONDUCT.md` updated to HAS-007 pipeline
- [ ] Gate 0 (Sync Gate) implemented in `scripts/git-sync.sh`
- [ ] Gate 1 (Constitution Gate) implemented in `scripts/constitution-gate.py`
- [ ] All existing process templates remain valid
- [ ] `close-session.sh` updated to use new pipeline stages
- [ ] All existing tests pass after migration
