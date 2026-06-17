# Tasks: System Hardening & Bridge Fix

## Task 1 — Commit fixes existentes
- [ ] git add src/core/neo4j_store.py webui/routes/__init__.py src/core/unified_bridge.py src/core/verify.py
- [ ] git add tests/unit/test_*.py
- [ ] git add DOCUMENTO_DE_ERRORES.md
- [ ] git add scripts/automation/
- [ ] git add state/
- [ ] git commit -m "[006] System hardening: memory fix, keys→env, Qdrant wiring, tests +33, auto-save"

## Task 2 — Verificar WhatsApp bridge port
- [ ] Confirmar bridge en 3002 (ya verificado)
- [ ] Verificar que `webui/routes/__init__.py` usa el puerto correcto (3001 está bien porque 3001 = hermes_wa auth, 3002 = bridge API)

## Task 3 — Push workflow-enforcer skill
- [ ] git add .openclaw/workspace/skills/workflow-enforcer/
- [ ] git add specs/006-system-hardening/
- [ ] git commit -m "[006] Workflow-enforcer skill + SDD spec 006"

## Task 4 — Verify final
- [ ] Correr test suite completa
- [ ] Verificar cobertura
- [ ] Verificar bridges via preflight
- [ ] Verificar commit subido a GitHub

## Task 5 — Archive
- [ ] Actualizar DOCUMENTO_DE_ERRORES.md con el fix de WhatsApp bridge


## Session 2026-06-12: AzREC + Content Pipeline + Telegram

- [X] T017 Configurar nginx con locations para AzREC y productos
- [X] T018 Crear close-session.sh para guardar estado entre sesiones
