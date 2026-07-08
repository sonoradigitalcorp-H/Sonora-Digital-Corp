# HAS-001 — Hermes Architecture Standard: Constitution Engine

**Status:** Draft v1
**Domain:** governance
**Updated:** 2026-07-08
**Depends on:** HAS-000
**Replaces:** `truth/` directory

---

## 1. Purpose

Define the structure, contracts, and migration path for the system's constitution. The Constitution is the set of laws that govern every action in the system — no agent, skill, or human operates outside it.

---

## 2. Constitution Structure

```
constitution/
├── 00-index.yaml              # Catalog of all constitution files
├── 01-mission.yaml            # Mission statement, north star, purpose
├── 02-vision.yaml             # Long-term vision, what success looks like
├── 10-principles.yaml         # Immutable principles of the system
├── 20-engineering.yaml        # Engineering standards, methodology
├── 30-architecture.yaml       # Architectural decisions, patterns, contracts
├── 40-security.yaml           # Security policies, encryption, access
├── 50-quality.yaml            # Quality standards, test coverage, linting
├── 60-agents.yaml             # Agent behavior rules, capability boundaries
├── 70-memory.yaml             # Memory policies, retention, privacy
├── 80-events.yaml             # Event schemas, required fields, catalog
├── 90-governance.yaml         # Constitution Engine: gates, policies, audits
├── 100-cost.yaml              # Cost policies, budgets, model routing
├── 110-brand.yaml             # Brand guidelines, tone, visual identity
├── 120-ux.yaml                # UX principles, Orb states, interaction rules
└── 130-ethics.yaml            # Ethical boundaries, content policies
```

### YAML Contract

Every constitution file follows this exact schema:

```yaml
version: 1
domain: <domain_name>
updated: <ISO8601>
level: <0-5>          # 0=immutable, 5=ephemeral
rules:
  - id: "<DOMAIN>-NNN"
    description: "Human-readable rule"
    category: <category>
    severity: error | warning | info
    applies_to:
      - all_agents
      - <specific_agent>
      - human
    enforcement: automated | semi-automated | manual
    check: "<path to validation script or 'manual'>"
    detail: "<optional multi-line context>"
```

### Level System

| Level | Stability | Change Process | Example |
|---|---|---|---|
| 0 | Immortal | Requires RFC + full pipeline | Principles, Mission |
| 1 | Stable | Requires ADR + review | Architecture, Security |
| 2 | Managed | Requires update + commit | Infrastructure |
| 3 | Flexible | Can change per sprint | Coding conventions |
| 4 | Ephemeral | Can change anytime | Agent-specific rules |
| 5 | Dynamic | Generated automatically | Evolution Engine outputs |

---

## 3. Constitution Engine

The Constitution Engine is a set of gates that validate every action before, during, and after execution.

### Gate Pipeline

```
Agent Action Request
    │
    ▼
┌─────────────────────────────┐
│ 1. POLICY GATE              │
│    - Does agent have permission? │
│    - Is action in capability scope? │
│    - constitution/60-agents.yaml  │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ 2. SECURITY GATE            │
│    - Secrets exposed?        │
│    - Network binding safe?   │
│    - constitution/40-security.yaml │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ 3. COST GATE                │
│    - Budget remaining?       │
│    - Model selection optimal?│
│    - constitution/100-cost.yaml   │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ 4. COMPLIANCE GATE          │
│    - Follows constitution?   │
│    - Events emitted?        │
│    - ALL constitution/ rules │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ 5. QUALITY GATE             │
│    - Tests pass?            │
│    - Coverage ≥ threshold?  │
│    - Lint clean?            │
│    - constitution/50-quality.yaml │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ 6. KNOWLEDGE GATE           │
│    - Similar past work?     │
│    - Lessons applied?       │
│    - Memory consulted?      │
│    - constitution/70-memory.yaml  │
└─────────────────────────────┘
    │
    ▼
          EXECUTION
    │
    ▼
┌─────────────────────────────┐
│ 7. AUDIT                    │
│    - Event emitted          │
│    - Log written            │
│    - Metric recorded        │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ 8. LEARNING                 │
│    - Score computed         │
│    - Lesson extracted       │
│    - ADR generated (if needed)│
└─────────────────────────────┘
```

### Script: `scripts/constitution-gate.py`

Replaces `scripts/verify-gate.py`. Runs all 6 pre-execution gates:

```bash
python3 scripts/constitution-gate.py --plan process/active/PLAN.yaml
```

Output: PASS/FAIL per gate + violations list. If any gate fails → STOP.

---

## 4. Migration: `truth/` → `constitution/`

### Step 1: Map existing truth files to new structure

| Current `truth/` | New `constitution/` | Action |
|---|---|---|
| `00-index.yaml` | `00-index.yaml` | Copy + add level field |
| `10-principles.yaml` | `10-principles.yaml` | Copy (maintains level 0) |
| `20-architecture.yaml` | `30-architecture.yaml` | Copy + add covenant rules |
| `30-security.yaml` | `40-security.yaml` | Copy + expand |
| `40-infrastructure.yaml` | `30-architecture.yaml` | Merge into architecture |
| `45-execution.yaml` | `90-governance.yaml` | Move to governance |
| `50-coding.yaml` | `20-engineering.yaml` | Move + expand |
| `60-git.yaml` | `20-engineering.yaml` | Merge into engineering |
| `70-documentation.yaml` | `20-engineering.yaml` | Merge into engineering |
| `80-operations.yaml` | `90-governance.yaml` | Merge into governance |
| `85-compliance.yaml` | `90-governance.yaml` | Merge into governance |
| `90-learned.yaml` | `90-governance.yaml` | Merge as "lessons" section |

### Step 2: Create new files with additional domains

- `01-mission.yaml` — extract from AGENTS.md and OMEGA-PROMPT
- `02-vision.yaml` — extract from session conversations + vision
- `50-quality.yaml` — extract from CONDUCT.md and testing standards
- `60-agents.yaml` — extract from agent behaviors
- `70-memory.yaml` — new (memory policies)
- `80-events.yaml` — new (event schemas)
- `100-cost.yaml` — new (cost policies)
- `110-brand.yaml` — new (brand guidelines)
- `120-ux.yaml` — new (UX principles)
- `130-ethics.yaml` — new (ethical boundaries)

### Step 3: Migration Script

Create `scripts/migrate-constitution.sh`:

```bash
#!/bin/bash
# Migrate truth/ → constitution/
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# 1. Copy existing truth files with mapping
cp "$ROOT/truth/00-index.yaml" "$ROOT/constitution/00-index.yaml"
cp "$ROOT/truth/10-principles.yaml" "$ROOT/constitution/10-principles.yaml"
cp "$ROOT/truth/20-architecture.yaml" "$ROOT/constitution/30-architecture.yaml"
cp "$ROOT/truth/30-security.yaml" "$ROOT/constitution/40-security.yaml"
# ... etc

# 2. Create new files from templates
for domain in mission vision quality agents memory events cost brand ux ethics; do
  if [ ! -f "$ROOT/constitution/$domain.yaml" ]; then
    cat > "$ROOT/constitution/$domain.yaml" << EOF
version: 1
domain: $domain
updated: $(date -u +%Y-%m-%dT%H:%M:%SZ)
level: 3
rules: []
EOF
  fi
done

# 3. Update symlinks and references
echo "Constitution migration complete."
echo "NOTE: truth/ still exists for backward compat. Remove when all references updated."
```

### Step 4: Backward compatibility

During migration, maintain a symlink so old scripts still work:

```bash
ln -sf ../constitution truth
```

After 1 month of zero errors from old scripts, remove `truth/` entirely.

---

## 5. Validation

The Constitution Engine validates itself:

```bash
python3 scripts/validate-constitution.py
```

Checks:
- Every YAML file matches the schema
- No duplicate rule IDs
- All `applies_to` agents exist in agent registry
- All `check` paths exist
- Cross-references between files are valid

---

## 6. Success Criteria

- [ ] `constitution/` directory exists with all 15 files
- [ ] `truth/` is symlinked to `constitution/` for backward compat
- [ ] `scripts/constitution-gate.py` replaces `verify-gate.py`
- [ ] All 6 gates execute and validate correctly
- [ ] `scripts/validate-constitution.py` passes with 0 violations
- [ ] `scripts/migrate-constitution.sh` runs idempotently
- [ ] All existing tests pass
- [ ] `close-session.sh` uses constitution-gate instead of verify-gate

---

## 7. Risks

| Risk | Mitigation |
|---|---|
| Old scripts reference `truth/` directly | Symlink + deprecation warning in log |
| Too many files to maintain | Level system: only level 0-1 require strict validation |
| Migration breaks CI | Run migrate script in dry-run mode first |
| Constitution becomes too large | Split into `constitution/` directory with index — not a monolith |
