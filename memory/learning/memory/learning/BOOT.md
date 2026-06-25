# Learning Loop - Quick Boot Reference

You have a structured self-improvement system. This file is a quick reference.

## Critical Rules
Read `rules.json` for full details. Key rules:
1. Write important facts to file IMMEDIATELY
2. Save findings every 2 significant operations
3. Write learning events after debugging sessions

## After Actions
- Debugged something? Append to `events.jsonl`
- Made a mistake? Update `rules.json`
- Learned something new? Update relevant files AND events.jsonl

## File Locations
- Events: `memory/learning/events.jsonl` (append-only JSONL)
- Rules: `memory/learning/rules.json` (read at boot)
- Lessons: `memory/learning/lessons.json` (intermediate tier)
- Checklist: `memory/learning/pre-action-checklist.md` (check before risky actions)
- Metrics: `memory/learning/metrics.json` (weekly tracking)

## v1.4.0 New Features
- **Confidence Decay:** Rules lose confidence over time. Run `confidence-decay.sh` weekly.
- **Cross-Agent Sharing:** Export/import rules with other agents.
- **Anomaly Detection:** Automatic spike detection in event patterns.
- **Parse Error Logging:** JSON errors are logged to `parse-errors.jsonl`.

## Quick Commands
```bash
# Check rule confidence
bash confidence-decay.sh

# Export rules for sharing
bash export-rules.sh --output my-rules.json

# Import rules from another agent
bash import-rules.sh other-agent-rules.json --dry-run  # preview first
bash import-rules.sh other-agent-rules.json            # actually import
```
