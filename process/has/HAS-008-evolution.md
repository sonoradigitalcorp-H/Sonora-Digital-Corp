# HAS-008 — Hermes Architecture Standard: Evolution Engine

**Status:** Draft v1
**Domain:** evolution
**Updated:** 2026-07-08
**Depends on:** HAS-003, HAS-004, HAS-007

---

## 1. Purpose

Define the Evolution Engine — the meta-agent that observes system health, generates ADRs, proposes refactors, and updates prompts automatically. The engine that makes the system improve itself.

---

## 2. Architecture

```
                    ┌──────────────────────────────────────────┐
                    │           EVENT BUS (HAS-003)             │
                    │  commits · errors · scores · deploys ·   │
                    │  agent failures · cost spikes · drifts   │
                    └──────────────────┬───────────────────────┘
                                       │
                                       ▼
                    ┌──────────────────────────────────────────┐
                    │          1. OBSERVER                      │
                    │     Listens to events, feeds metrics      │
                    │     Maintains health dashboard            │
                    └──────────────────┬───────────────────────┘
                                       │
                                       ▼
                    ┌──────────────────────────────────────────┐
                    │          2. SCORECARD                     │
                    │     System health score (0-100)           │
                    │     Per-agent scores                      │
                    │     Trend detection (improving/decaying)  │
                    └──────────────────┬───────────────────────┘
                                       │
                          ┌────────────┴────────────┐
                          │                         │
                          ▼                         ▼
          ┌──────────────────────────┐  ┌──────────────────────────┐
          │ 3. ERROR DETECTOR        │  │ 4. IMPROVEMENT PROPOSER  │
          │ Pattern detection in     │  │ Generates RFCs/ADRs      │
          │ failures, regressions    │  │ when score < threshold   │
          │ New error types          │  │ Suggests refactors       │
          └──────────┬───────────────┘  └──────────┬───────────────┘
                     │                             │
                     └─────────────┬───────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────────────────┐
                    │          5. ADR GENERATOR                 │
                    │     Writes ADR to process/rfcs/           │
                    │     Includes: problem, solution, score,   │
                    │     risk analysis                         │
                    └──────────────────┬───────────────────────┘
                                       │
                                       ▼
                    ┌──────────────────────────────────────────┐
                    │          6. PROMPT UPDATER                │
                    │     Updates agent prompts based on        │
                    │     lessons learned                       │
                    │     Version-controls prompt changes       │
                    └──────────────────┬───────────────────────┘
                                       │
                                       ▼
                    ┌──────────────────────────────────────────┐
                    │          7. AUTO-DOC                     │
                    │     Updates SPEC, SCORE, ADR, LECCION,   │
                    │     Gherkin automatically                │
                    └──────────────────┬───────────────────────┘
                                       │
                                       ▼
                    ┌──────────────────────────────────────────┐
                    │          8. REFLECTOR                     │
                    │     Evaluates own proposals               │
                    │     If adopted: score improvement         │
                    │     If rejected: learn why                │
                    └──────────────────────────────────────────┘
```

---

## 3. Module Descriptions

### 3.1 Observer

Listens to the Event Bus (HAS-003) for system events. Maintains a health dashboard:

```python
class EvolutionObserver:
    async def listen(self):
        """Subscribe to event bus, process relevant events."""

    def health(self) -> SystemHealth:
        """Current system health score+ details."""
```

Metrics tracked:
- Test pass rate (last 24h)
- Error rate by agent
- Cost per operation (trending up/down)
- Agent latency (p50, p95, p99)
- Constitution gate pass/fail ratio
- Deploy frequency

### 3.2 Scorecard

Computes system health:

```python
@dataclass
class Scorecard:
    overall: int                      # 0-100
    by_dimension: dict[str, int]      # test_health, cost_health, error_health, etc.
    trends: dict[str, str]            # improving | stable | decaying
    recommendations: list[str]
```

### 3.3 Error Detector

Pattern-matches failures to known error types:

| Pattern | Action |
|---|---|
| Same test failing >3x | Propose test fix |
| Agent timeout >10% | Propose model downgrade/faster agent |
| Cost spike >2x normal | Propose model change (smaller model) |
| Gate failure repeated | Propose constitution update |
| Disk >85% | Propose cleanup workflow |
| Memory leak | Propose restart schedule |

### 3.4 Improvement Proposer

Generates RFCs when score drops below threshold:

```python
@dataclass
class RFC:
    id: str
    title: str
    problem: str
    proposed_solution: str
    expected_impact: str
    risk: str
    score: int                      # confidence 0-100
    generated_by: str               # agent that generated it
```

### 3.5 ADR Generator

Generates structured ADRs for accepted RFCs:

```python
@dataclass
class ADRDraft:
    title: str
    status: str                     # proposed | accepted | deprecated
    context: str                    # What prompted this decision
    decision: str                   # What was decided
    consequences: list[str]         # Positive + negative
    alternatives: list[str]         # Options considered
    score: int                      # Confidence score
```

### 3.6 Prompt Updater

Tracks prompt versions and updates them:

```
prompts/
├── versions/
│   ├── v1.0/                      # Original prompts
│   ├── v1.1/                      # First update (from Evolution Engine)
│   └── v2.0/                      # Major revision
├── changelog.md
└── current -> v1.1/               # Symlink to active version
```

### 3.7 Auto-Doc

Generates documentation from events + execution results. Replaces manual `close-session.sh` steps:

```python
class AutoDoc:
    async def generate_spec(self, mission: str, execution_result: ExecutionResult):
        """Generate SPEC.md from mission + results."""

    async def generate_score(self, execution_result: ExecutionResult):
        """Generate SCORE.md automatically."""

    async def generate_lesson(self, execution_result: ExecutionResult):
        """Generate LECCION.md from reflection."""

    async def generate_gherkin(self, spec, test_results):
        """Generate Gherkin feature file from test results."""
```

---

## 4. Evolution Engine Output Files

```
process/rfcs/                        # RFCs from Improvement Proposer
├── RFC-20260708-001.md
├── RFC-20260708-002.md
└── ...

process/adrs/                        # ADRs from ADR Generator
├── ADR-20260708-001.md
└── ...

evolution/
├── scorecard.json                    # Current system health score
├── history.jsonl                     # Score over time
├── prompt-changelog.md               # Prompt version history
└── metrics/                          # Detailed metrics
    ├── test-pass-rate.json
    ├── cost-by-agent.json
    └── error-rates.json
```

---

## 5. Triggering the Evolution Engine

### Automatic (cron)
- Runs every 6 hours via `scripts/evolution-cron.sh`
- Checks scorecard, generates RFCs if score < 70

### Manual
```bash
python3 -m evolution.main --mode check     # Check health only
python3 -m evolution.main --mode propose   # Generate RFCs if needed
python3 -m evolution.main --mode full      # Full cycle: observe→propose→generate→update
```

### Post-Session
```bash
scripts/close-session.sh --auto-evolve     # Also run Evolution Engine
```

---

## 6. Evolution Events

| Event | Trigger | Payload |
|---|---|---|
| `evolution.score.updated` | Scorecard computed | `{ overall, by_dimension }` |
| `evolution.rfc.generated` | RFC written | `{ id, title, score }` |
| `evolution.adr.generated` | ADR written | `{ id, title, status }` |
| `evolution.prompts.updated` | Prompts version changed | `{ agent, old_version, new_version }` |
| `evolution.docs.generated` | Auto-doc ran | `{ session_id, files_generated }` |
| `evolution.refactor.proposed` | Refactor suggested | `{ target, reason, impact }` |

---

## 7. Directory Structure

```
evolution/
├── __init__.py
├── main.py                       # Entry point
├── observer.py                   # Event listener
├── scorecard.py                  # Health scoring
├── error_detector.py             # Pattern matching
├── proposer.py                   # RFC generation
├── adr_generator.py              # ADR generation
├── prompt_updater.py             # Prompt versioning
├── auto_doc.py                   # Automatic documentation
├── reflector.py                  # Self-evaluation
├── models.py                     # RFC, ADRDraft, Scorecard
├── prompts/
│   ├── versions/
│   │   └── v1.0/                 # Initial prompts
│   └── changelog.md
└── tests/
    ├── test_observer.py
    ├── test_scorecard.py
    ├── test_error_detector.py
    ├── test_proposer.py
    ├── test_adr_generator.py
    └── test_auto_doc.py
```

---

## 8. Migration

The Evolution Engine replaces and extends:

| Old Component | New Module | Action |
|---|---|---|
| `scripts/auto-doc.py` | `evolution/auto_doc.py` | Move + extend |
| `scripts/verify-gate.py` | `evolution/scorecard.py` | Move scoring logic |
| `close-session.sh` (doc steps) | `evolution/auto_doc.py` | Delegate doc generation |
| `memory/learning/` | `evolution/observer.py` + `proposer.py` | Move learning logic |
| `process/completed/` docs | `evolution/auto_doc.py` | Generate automatically |

---

## 9. Success Criteria

- [ ] `evolution/main.py` runs as standalone module
- [ ] Observer listens to event bus and tracks metrics
- [ ] Scorecard computes system health (0-100)
- [ ] Error detector catches repeated failures
- [ ] Proposer generates RFCs when score < 70
- [ ] ADR generator produces valid ADR.md files
- [ ] Prompt updater versions prompts and maintains changelog
- [ ] Auto-doc generates SPEC, SCORE, ADR, LECCION, Gherkin from events
- [ ] `scripts/evolution-cron.sh` triggers automatic run every 6h
- [ ] All existing tests pass after migration
