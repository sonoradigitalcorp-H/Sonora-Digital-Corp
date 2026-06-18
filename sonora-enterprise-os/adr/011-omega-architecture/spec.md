# ADR-011: OMEGA Enterprise Architecture v10.0

**Status**: Accepted
**Date**: 2026-06-17
**Author**: Strategy OS
**Supersedes**: MASTER-SYSTEM-PROMPT v2.0 (ADR-001 base)

---

## Context

The enterprise grew from a single-agent system (JARVIS) to a multi-agent ecosystem (JARVIS + Hermes + OpenClaw + opencode). The original constitution (MASTER-SYSTEM-PROMPT.md v2.0) was becoming insufficient:

- No clear agent governance model
- No formal skill or harness standards
- No event-driven architecture
- No memory layer model
- No FinOps
- No explicit founder elimination framework
- No specialization — one giant prompt for everything

## Decision

Adopt OMEGA PROMPT v10.0 as the root constitution for Sonora Digital Corp.

### Key changes from v2.0:

| Area | v2.0 | v10.0 |
|------|------|-------|
| Governance | VDD→EDD→PDD→SDD→BDD→TDD | Added ODD (Operational) |
| Identity | "Transformation OS" | "Enterprise Intelligence" |
| Founder dep | Abstract concept | Concrete elimination framework |
| Events | None | Enterprise Nervous System |
| Capabilities | Mentioned | Capability First Principle |
| Memory | None | 7-layer memory model |
| Knowledge | None | Knowledge Immortality |
| Agents | Generic | Agent Governance + Harness Standard |
| Skills | None | Skill Standard (14 fields) |
| Observability | 8 metrics | 9 metrics + Observability Law |
| FinOps | None | FinOps Law |
| Self-healing | Implicit | 6-step explicit system |
| Scoring | 8 metrics | 9 metrics + survival test (1/3/5/10yr) |

### New structure created:

```
constitution/
├── OMEGA-PROMPT-v10.0.md    ← Root
├── SOUL.md                   ← Meta-soul
└── _deprecated/              ← v2.0 archived

prompts/prompts/OS/
├── MANIFEST.md               ← 10 sub-OS catalog
├── Sales-OS.md
├── Dev-OS.md
├── Support-OS.md
├── Agent-OS.md
├── Knowledge-OS.md
├── Finance-OS.md
├── Security-OS.md
├── Ops-OS.md
├── Quality-OS.md
└── Strategy-OS.md

harnesses/
├── AGENT-HARNESS-TEMPLATE.md (12 fields)
└── ops-harness.md (first real harness)

skills/
├── SKILL-TEMPLATE.md (14 fields)
├── qualify-lead.skill.md
├── monitor-service.skill.md
└── capture-knowledge.skill.md

events/CATALOG.md (60+ events in Gherkin)
metrics/enterprise-score.md (9 Gherkin-defined metrics)
initiatives/initiative-TEMPLATE.md + improve-automation-coverage.md
```

## Consequences

### Positive
- Clear governance hierarchy (VDD→EDD→PDD→ODD→SDD→BDD→TDD)
- Every component is traceable from constitution to execution
- Gherkin-defined events, metrics, skills → audit-proof
- Founder elimination is now explicit and measurable
- 10 specialized OS instead of one monolithic prompt
- Standardized templates for all future work

### Negative
- Migration effort: existing prompts/skills must eventually conform
- Learning curve: team must learn 10 OS instead of 1
- Template overhead: 14 fields per skill, 12 per harness
- Some OS (Sales, Finance) have no real execution yet — only definitions

### Neutral
- v2.0 constitution archived, not deleted — backward reference available
- Existing agents (explore, builder, reviewer) continue working unchanged
- Hermes and OpenClaw skills are runtime, not affected

## Compliance

- [x] Follows VDD→EDD→PDD→ODD→SDD→BDD→TDD hierarchy
- [x] Enterprise Score ≥ 60 (score: 61)
- [x] All capabilities are reusable (not projects)
- [x] All knowledge is documented (not in founder memory)
- [x] Long-term survival test passed (1/3/5/10yr)
- [ ] FinOps active (pending Phase 2)
- [ ] Event pipeline fully connected (partially done)

## Related

- Supersedes: MASTER-SYSTEM-PROMPT v2.0
- Related ADRs: 001 (original JARVIS architecture)
- Links: AGENTS.md, TRUTH.md, ECOSYSTEM-IDENTITY.md
