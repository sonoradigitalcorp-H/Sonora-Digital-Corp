---
id: 010
title: Daily Error Correction & Self-Healing
status: draft
type: automation
---

# Spec 010 — Daily Error Correction & Self-Healing

## Purpose
Automated daily system that finds, logs, and fixes errors. Runs at 4AM daily.
Learns from DOCUMENTO_DE_ERRORES.md and prevents regression.

## Architecture

| Component | Role |
|-----------|------|
| `scripts/daily-error-correction.sh` | Main script, run by systemd timer |
| `/etc/systemd/system/jarvis-error-correction.service` | Service unit |
| `/etc/systemd/system/jarvis-error-correction.timer` | Timer unit (4AM daily) |
| `DOCUMENTO_DE_ERRORES.md` | Error registry with status |
| Specs 001-010 | Source of truth for verification |

## Error Categories & Fixes

### Category A: Duplicates & Redundancy
- Duplicate cron entries → unify
- Duplicate n8n workflow files → deduplicate
- Duplicate script executions → merge

### Category B: Broken Configurations
- Invalid JSON in workflows → validate and fix
- Missing trigger nodes → add or disable
- Container exit codes → diagnose and restart

### Category C: Service Health
- Check all systemd services → restart failed ones
- Check Docker containers → restart exited ones
- Check port availability → resolve conflicts

### Category D: Data Integrity
- Qdrant garbage entries → clean
- Neo4j consistency → verify
- Git sync status → check

## Verification
- [ ] Script runs without errors at 4AM
- [ ] All systemd services healthy after run
- [ ] No duplicate cron entries
- [ ] All n8n workflows valid JSON
- [ ] DOCUMENTO_DE_ERRORES.md updated with findings
