# Spec: Base System Setup

- **Status**: Approved
- **Author**: @mystic
- **Revenue Gate**: ✅ (foundation for all future revenue)
- **Priority**: P0
- **Estimated Effort**: 5 story points

## 1. Problem

Sonora Digital Corp and YAMI operate with fragmented infrastructure,
no shared constitution, no automated CI/CD, and no unified development
workflow. Both agents (Mystic and Noel) work independently without
a common spec-driven process, leading to duplicated effort,
undocumented decisions, and no systematic learning.

Without a base system, every future feature will be ad-hoc,
untested, and unreviewed.

## 2. Goal

Establish a shared, spec-driven development ecosystem in a single repo
with constitution, templates, automated CI/CD, and a learning system.

## 3. Scope

### In scope

- Constitution: TRUTH.md + RULES.md
- Documentation: AGENTS.md, GLOSARIO.md, ONBOARDING.md
- Templates: spec, plan, tasks, DISCOVERY, feature, issue
- Scripts: analizador.py (autonomous scanner), implementador.sh (auto-implementer)
- CI/CD: ci.yml (lint+test), analizador.yml (cron 6h), implementador.yml (on Issue approved)
- GitHub config: ISSUE_TEMPLATE/feature.yml
- Memory: lecciones.json, patrones.md
- First spec: this file (001-setup-base)

### Out of scope

- Product-specific specs (MIRU, KIKU, TOMONI — future)
- Brain Gateway API (future)
- GBrain migration (future)
- Vercel deployment pipelines (future)

## 4. User Stories

```gherkin
Feature: Repository Constitution
  As a developer (Mystic or Noel)
  I want a shared constitution with a truth hierarchy and rules
  So that every decision has a clear reference point

  Scenario: Truth hierarchy is accessible
    Given I open constitution/TRUTH.md
    Then I see the hierarchy from CLIENT REQUEST down to ASSUMPTIONS
    And I see the 7 truth rules

  Scenario: Rules are defined
    Given I open constitution/RULES.md
    Then I see exactly 10 absolute rules
    And each rule has a clear statement

Feature: Spec-Driven Development
  As a developer
  I want standardized templates for specs, plans, and tasks
  So that every feature follows the same process

  Scenario: Spec template exists
    Given I open templates/spec-template.md
    Then I see sections for Problem, Goal, Scope, User Stories, Technical Approach, Dependencies, Risks, Acceptance Criteria

  Scenario: Plan template exists
    Given I open templates/plan-template.md
    Then I see task breakdown by phase

  Scenario: Task template exists
    Given I open templates/tasks-template.md
    Then I see acceptance criteria per task

Feature: Autonomous Repo Scanner
  As a developer
  I want an automated scanner that checks repo health every 6 hours
  So that missing specs and issues are caught early

  Scenario: Scanner finds missing spec
    Given there is an app in apps/ with no corresponding spec in specs/
    When analizador.py runs
    Then it creates an Issue with label "spec-needed"

  Scenario: Scanner finds no issues
    Given all apps have corresponding specs
    When analizador.py runs
    Then it reports "No issues found"

Feature: Automated Implementation
  As a developer
  I want an implementation bot that builds features from approved specs
  So that I only need to review and approve

  Scenario: Issue approved triggers implementation
    Given an Issue exists with label "approved"
    And the Issue body references a spec path
    When implementador.sh runs
    Then it creates a branch, implements the spec, and opens a PR

  Scenario: Missing spec blocks implementation
    Given an Issue has label "approved"
    But no spec path is referenced
    When implementador.sh runs
    Then it exits with error "No spec found"
```

## 5. Technical Approach

### Repository Structure
```
constitution/       → TRUTH.md, RULES.md
docs/               → GLOSARIO.md, ONBOARDING.md
templates/          → spec, plan, tasks, DISCOVERY, feature, issue
scripts/            → analizador.py, implementador.sh
.github/
  workflows/        → ci.yml, analizador.yml, implementador.yml
  ISSUE_TEMPLATE/   → feature.yml
memory/             → lecciones.json, patrones.md
specs/<n>-<name>/   → spec.md, plan.md, tasks.md
apps/               → product directories
```

### Automation Flow
1. **Analizador** (cron 6h): reads memory + scans apps → creates Issues
2. **Human** reviews Issue → sets label "approved" if valid
3. **Implementador** (on label): reads spec → implements with OpenCode → opens PR
4. **Human** reviews PR → merges → lesson written to memory

### CI Pipeline
- Push/PR to main: validate
  - Python lint (flake8)
  - pytest with coverage ≥ 80%
  - Structure validation (dirs, files)
  - Spec structure check (has User Stories + Acceptance Criteria)

## 6. Dependencies

- GitHub: repo, Actions, Issues, branch protection
- OpenCode: installed on developer machines
- Python 3.10+
- OpenRouter: API key for both developers

## 7. Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Noel doesn't follow spec-first | H | M | CI enforces spec checks; branch protection blocks direct pushes |
| Automated PRs bypass review | H | L | Branch protection requires 1 approval; implementador opens PR, doesn't merge |
| Analizador creates noise | M | M | Issues created with labels; human can close noisemakers |
| OpenCode breaks between versions | M | L | Pin version in scripts; document upgrade process |

## 8. Acceptance Criteria

- [x] constitution/TRUTH.md exists with truth hierarchy and 7 rules
- [x] constitution/RULES.md exists with 10 absolute rules
- [x] docs/GLOSARIO.md defines all key terms
- [x] docs/ONBOARDING.md guides Noel to start
- [x] AGENTS.md documents roles and protocol
- [x] All 6 templates exist in templates/
- [x] .github/ISSUE_TEMPLATE/feature.yml is configured
- [x] scripts/analizador.py runs without errors
- [x] scripts/implementador.sh is executable
- [x] ci.yml runs lint + test + structure validation
- [x] analizador.yml runs on cron 6h
- [x] implementador.yml triggers on Issue label "approved"
- [x] memory/lecciones.json has initial lessons
- [x] memory/patrones.md has initial patterns
- [x] specs/001-setup-base/spec.md is this file
