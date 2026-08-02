# Long-Term Survival Test

**Inherits**: OMEGA PROMPT v10.0 + SOUL.md
**Version**: 1.0.0
**Audit ID**: METRICS-SURVIVAL-001

---

Every proposal must evaluate long-term impact across 5 dimensions.

## Evaluation Framework

### 1 Year Impact

| Question | Answer (0-10) |
|----------|---------------|
| Will this generate revenue within 12 months? | |
| Will this reduce founder dependency within 12 months? | |
| Will this increase automation within 12 months? | |
| Can this be implemented without new dependencies? | |

### 3 Year Impact

| Question | Answer (0-10) |
|----------|---------------|
| Will this still be relevant in 3 years? | |
| Can this survive vendor/model changes? | |
| Has this been designed for reuse? | |
| Is the knowledge preserved (ADR, playbooks)? | |

### 5 Year Impact

| Question | Answer (0-10) |
|----------|---------------|
| Will this still generate value in 5 years? | |
| Can it operate without founder intervention? | |
| Can it scale 10x without redesign? | |
| Are all dependencies replaceable? | |

### 10 Year Impact

| Question | Answer (0-10) |
|----------|---------------|
| Would this survive if the company pivots? | |
| Would this survive a major technology shift? | |
| Is the data model extensible for unknown future needs? | |
| Could this become a product/marketplace asset? | |

### Survivability

| Question | Answer (0-10) |
|----------|---------------|
| How many single points of failure exist? | |
| Can this recover from total data loss? | |
| Does this depend on any specific individual? | |
| Does this depend on any external paid service? | |

### Recovery Complexity

| Question | Answer (0-10) |
|----------|---------------|
| How long to fully restore after catastrophic failure? | |
| Is there a documented recovery procedure? | |
| Has the recovery procedure been tested? | |

## Final Verdict

| Score | Verdict |
|-------|---------|
| ≥ 8/10 | Strong — approve |
| 6-7/10 | Acceptable — approve with monitoring |
| 4-5/10 | Weak — require improvements |
| < 4/10 | Kill or reject |
