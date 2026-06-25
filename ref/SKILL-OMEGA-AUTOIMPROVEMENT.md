---
name: omega-autoimprovement
description: "Self-improvement system for OMEGA agent. Use every session to: (1) Load rules from memory/learning/rules.json at boot, (2) Capture events after any mistake/success/feedback, (3) Check pre-action-checklist before risky operations, (4) Run pattern extraction after debugging sessions. Never start a session without loading the learning loop."
---

# OMEGA Auto-Improvement Skill

## Boot Sequence (Every Session)

1. Read `rules.json` — hard behavioral constraints
2. Read `BOOT.md` — quick reference
3. Run `pre-action-checklist.sh` before any risky action
4. After mistakes: append to `events.jsonl` within 60s

## Rule Types

- **MUST**: Hard constraint. Never violate. (e.g., "Always use APA citations")
- **NEVER**: Absolute prohibition. (e.g., "Never use fake data")
- **PREFER**: Strong recommendation. Violate only with explicit user approval.

## Current Rules (14 active)

See `memory/learning/rules.json` for full list. Key rules:
- R-001: Apple design for public landing pages
- R-002: Speed mode on urgency keywords
- R-007: OMEGA pipeline always
- R-011: Real data only

## Event Capture Format

```json
{"ts":"ISO_TIMESTAMP","type":"mistake|success|feedback|discovery|debug_session","category":"design|code|infrastructure|knowledge|communication","tags":[],"problem":"what happened","solution":"how to fix","confidence":"proven|probable|hypothetical","source":"session-YYYY-MM-DD"}
```

## Weekly Maintenance

```bash
bash detect-patterns.sh
bash confidence-decay.sh
bash promote-rules.sh
bash self-audit.sh
bash update-metrics.sh
```

## Failure Modes

- **Forgetting to load rules**: Rules MUST be loaded at boot. If skipped, agent repeats mistakes.
- **Not capturing events**: If an error happens and isn't logged, it will happen again. Capture within 60s.
- **Ignoring confidence scores**: Rules with confidence <0.5 need review. Don't trust stale rules.
