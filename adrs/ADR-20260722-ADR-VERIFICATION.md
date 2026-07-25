---
id: ADR-20260722-ADR-VERIFICATION
title: ADR/Spec Verification System — Real-Time Compliance Checking
status: accepted
date: 2026-07-22
---

# ADR — ADR/Spec Verification System

| Campo | Valor |
|-------|-------|
| **ID** | ADR-20260722-ADR-VERIFICATION |
| **Fecha** | 2026-07-22 |
| **Estado** | aceptado |

## Context

Sonora Digital Corp has ~55 ADRs across `process/active/` and `adrs/`, but zero automated verification that:

1. ADR content is complete (required fields: ID, Fecha, Context, Decision, Options Considered, Consequences, Status)
2. Functional Requirements (FRs) in SPECs are covered by tests
3. Code changes do not contradict prior ADRs
4. ADR compliance against the actual codebase is never checked — the only gate is a binary existence check

This creates a gap in the governance pipeline: decisions are recorded but never enforced. The OMEGA-PROMPT mandates continuous verification and the constitution gate covers policy, security, cost, compliance, quality, and knowledge — but not ADR/Spec integrity.

Additionally, there is no mechanism to emit verification events to the event bus (`state/events/events.jsonl`), so the enterprise score cannot reflect verification health.

## Decision

Create a real-time ADR/Spec verification system with four components:

### 1. `scripts/verify-adr.py` — Content Validator + Coverage Checker
- `validate_adr_content()`: Checks all required fields, section headers, returns validity + score
- `validate_adr_compliance()`: Scans codebase for keywords/patterns mentioned in ADRs
- `validate_spec_coverage()`: For each FR in a SPEC, finds matching Gherkin scenarios and test functions
- `validate_all_adrs()`: Batch validation across all ADR directories with aggregate scoring

### 2. `.gitea/workflows/adr-verify.yml` — CI/CD Integration
- Runs on every push and pull_request
- Validates all ADRs, checks spec coverage, and verifies compliance
- Emits verification events on success/failure via `emit-verification-event.py`

### 3. `scripts/emit-verification-event.py` — Event Bus Integration
- Emits `adr.verified` and `spec.verified` events to the unified event bus
- Follows the same conventions as `scripts/emit-event.py`
- Enables enterprise score to track verification health

### 4. ADR Gate in `constitution-gate.py`
- Adds Gate 7: `verify_adr_gate` that runs `validate_all_adrs()` and blocks on invalid ADRs

## Options Considered

| Option | Pros | Cons |
|--------|------|------|
| Custom Python scripts (selected) | Full control, no dependencies, matches existing tooling style | Requires maintenance |
| pytest plugin | Integrates with existing test suite | Overhead for non-test verification, harder to use in CI independently |
| Gitea Action marketplace action | Zero code | No action exists for ADR content validation, vendor dependency |
| ADR parser library (e.g., adr-tools) | Existing ecosystem | Not Python-native, would add dependency, no spec coverage support |

## Consequences

### Positive
- ✅ Every ADR now has measurable content quality (score/100)
- ✅ FR-to-test traceability becomes visible per SPEC
- ✅ CI blocks pushes that would commit invalid ADRs
- ✅ Verification events flow to event bus, enabling dashboards and score
- ✅ ADR Gate prevents plans from proceeding with non-compliant decisions
- ✅ Reuses existing patterns: `emit-event.py`, constitution-gate, `argparse` CLI

### Negative
- ⚠️ Initial run on ~55 ADRs will likely show gaps (scores < 100)
- ⚠️ `validate_adr_compliance()` uses keyword matching — may produce false positives/negatives
- ⚠️ Spec coverage check only works if FRs follow `FR\d+` naming convention
- ⚠️ Requires Python 3.10+ in CI runner (available in Gitea runner)

### Mitigations
- Scores are reported but don't block CI initially (warning only) — only structural validity blocks
- Keyword matching can be refined with custom dictionaries per ADR
- FR convention is already enforced by SPEC template since 2026-07-03
- CI runner image can be pinned to `python:3.10-slim`

## Lessons
- No existing ADR had automated validation — the first run will establish the baseline
- Gherkin tags (`@fr1`, `@fr2`) are the most reliable FR-to-test link
- ~55 ADRs in 2 directories requires directory-aware scanning, not single-path logic

## Related
- Spec: `SPEC-20260722-ADR-VERIFICATION` (pending)
- Scripts: `scripts/verify-adr.py`, `scripts/emit-verification-event.py`
- Events: `adr.verified`, `spec.verified`
- Template: `process/templates/ADR.md`
- Constitution Gate: `scripts/constitution-gate.py` (Gate 7)
