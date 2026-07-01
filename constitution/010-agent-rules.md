# Agent Rules — Behavior & SDD Pipeline

**Source**: 10-RULES.md + AGENTS.md (migrated)
**Audit ID**: AGR-001

---

## 10 Absolute Rules {#ten-rules}

### 1. Spec First, Always {#spec-first}
No code without an approved `spec.md`. No exceptions. The spec must include Gherkin scenarios.

### 2. Tests Must Be Green {#tests-green}
All tests must pass before merge. CI enforces this. If tests fail, the PR is blocked. No force-push to skip.

### 3. Humans Decide {#humans-decide}
Every spec, ADR, and PR requires human approval. The agent proposes; the human disposes.

### 4. Everything in the Repo {#everything-in-repo}
Code, specs, ADRs, decisions, memory — all committed. If it's not committed, it's not real.

### 5. PR Required + 1 Approval {#pr-required}
Every change to `main` goes through a PR. Branch protection enforces at least 1 approval.

### 6. OpenCode Always {#opencode-primary}
The sole primary agent is OpenCode. No Copilot, no Claude Code, no Codex as primary.

### 7. Stack is Fixed {#stack-fixed}
Python 3.10+, pytest, GitHub Actions, OpenRouter. No tech change without an approved ADR.

### 8. Continuous Learning {#continuous-learning}
Every sprint, write lessons to memory. The agent reads memory before proposing specs.

### 9. Value First {#value-first}
Every feature must tie to a business metric. If it doesn't create value, it doesn't ship.

### 10. One Brain {#one-brain}
One repo, one truth, one constitution, many products. Products share infrastructure via MCP, not duplication.

## SDD Pipeline {#sdd-pipeline}

All work follows: Spec → Design → Apply → Verify → Archive.

Each phase has a dedicated agent: sdd-spec, sdd-design, sdd-apply, sdd-verify, sdd-archive.
The orchestrator is the sdd agent.

## Agent Autonomy Levels {#autonomy-levels}

| Level | Name | Description |
|-------|------|-------------|
| L0 | Manual | Human does every step |
| L1 | Assisted | Agent proposes, human approves |
| L2 | Supervised | Agent acts, human reviews |
| L3 | Delegated | Agent acts, human can override |
| L4 | Autonomous | Agent acts independently |

Default: L1 for specs/ADRs/PRs, L2 for implementation, L3 for monitoring.
