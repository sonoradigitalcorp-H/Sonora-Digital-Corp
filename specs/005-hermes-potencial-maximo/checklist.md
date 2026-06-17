# Implementation Checklist: Hermes One — Potencial Máximo

**Spec**: spec.md
**Created**: 2026-06-11

---

## Phase 1: Foundation

- [ ] CHK001 Config migrated v28 → v29 successfully
- [ ] CHK002 approvals.mode set to smart
- [ ] CHK003 streaming.enabled set to true
- [ ] CHK004 Gateway installed as systemd service
- [ ] CHK005 Gateway auto-starts on boot
- [ ] CHK006 Telegram messages work after restart
- [ ] CHK007 WhatsApp messages work after restart

## Phase 2: Web Search + Browser

- [ ] CHK008 ddgs package installed
- [ ] CHK009 web-ddgs plugin enabled
- [ ] CHK010 Chromium installed
- [ ] CHK011 Web search returns results (US1 acceptance)
- [ ] CHK012 Browser navigation works (US1 acceptance)

## Phase 3: Voice

- [ ] CHK013 faster-whisper installed
- [ ] CHK014 STT enabled and configured (local/base)
- [ ] CHK015 Voice transcription works in Telegram

## Phase 4: Kanban

- [ ] CHK016 3 profiles created (worker, cron, research)
- [ ] CHK017 Kanban board initialized
- [ ] CHK018 Task created and completed cross-profile (US3 acceptance)

## Phase 5: Memory + Cron

- [ ] CHK019 Memory enabled, fact persists across sessions (US4 acceptance)
- [ ] CHK020 User profile enabled
- [ ] CHK021 health-monitor cron active
- [ ] CHK022 system-resources cron active
- [ ] CHK023 jarvis-heartbeat cron active

## Phase 6: Fallback Provider

- [ ] CHK024 Fallback model/provider configured
- [ ] CHK025 Auxiliary vision configured
- [ ] CHK026 Failover works (US2 acceptance)

## Phase 7: Final

- [ ] CHK027 security.redact_secrets enabled
- [ ] CHK028 `hermes doctor` all green
- [ ] CHK029 All 6 US acceptance tests pass
- [ ] CHK030 Spec committed to git

---

## Notes
- Check items off as completed: `[x]`
- 30 items total
- Constitution Check: ✅ PASS
