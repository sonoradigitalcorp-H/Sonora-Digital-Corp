# Feature Specification: System Hardening & Bridge Fix

**Feature Branch**: `006-system-hardening`

**Created**: 2026-06-12

## Objective
Harden JARVIS system: fix silent memory bug, close public repo, move hardcoded keys to env vars, fix WhatsApp bridge port mismatch, wire Qdrant into UnifiedSystem, add auto-save 24/7, achieve >65% test coverage.

## Scope
1. **Security**: Repo made private, API key `MysticWA2026!` moved to env var
2. **Memory**: `save_memory()`/`get_memory()` added to `neo4j_store.py`, `search_memory()` parameter collision fixed
3. **Bridges**: Qdrant wired into `UnifiedSystem`, WhatsApp bridge port verified (3002 vs 3001)
4. **Automation**: Auto-save cron job + skill created
5. **Quality**: 33 new tests, coverage 64%→69%, Ollama started, 106 memories fed to Qdrant
6. **Specs**: 23 historical specs recovered as read-only at `/home/mystic/reference/specs/`
7. **Workflow**: Workflow-enforcer skill created to enforce SDD

## Out of Scope
- Full WhatsApp authentication (requires QR scan)
- OpenClaw service restart (preexisting issue)
- Chromadb install for agent-evolver
