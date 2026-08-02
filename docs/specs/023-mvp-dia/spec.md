# SPEC-20260802-MVP-DIA — MVP Session (3 horas)

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260802-MVP-DIA` |
| **Fecha** | 2026-08-02 |
| **Duración** | 3 horas |
| **Objetivo** | Stabilizar el sistema para producción: commit, tag, tests, validación |

---

## Context

El sistema tiene 30+ fixes aplicados hoy pero sin commit. Hay 27 test collection errors. El repo tiene 2M+ líneas sin commit. Necesitamos estabilizar para poder desplegar.

---

## Meta del Día (3 horas)

| Hora | Tarea | Entregable |
|------|-------|------------|
| 0:00-0:15 | **Commit + Tag** | `git commit` + `v1.0.0` tag |
| 0:15-1:30 | **Fix Test Errors** | 27 errors → 0 errors |
| 1:30-2:00 | **Validación** | `make test` pasa, syntax OK |
| 2:00-2:30 | **Docs update** | CHANGELOG actualizado con fixes |
| 2:30-3:00 | **Engram save** | Memoria de sesión guardada |

---

## Tasks

### T1: Commit + Tag (15 min)
- [ ] `git add` de archivos modificados
- [ ] `git commit -m "feat: v1.0.0 — security fixes, bot fixes, n8n cleanup, tests"`
- [ ] `git tag -a v1.0.0 -m "Release v1.0.0 - SDC Platform"`

### T2: Fix Test Errors (75 min)
- [ ] Ejecutar `python -m pytest tests/ --co -q 2>&1 | grep ERROR` para identificar los 27 errores
- [ ] Analizar cada error (import paths, missing modules)
- [ ] Fixear imports en `tests/unit/test_unified_bridge.py`
- [ ] Fixear imports en `tests/unit/test_verify.py`
- [ ] Fixear imports en `tests/unit/test_voice.py`
- [ ] Fixear cualquier otro error de collection
- [ ] Verificar que `python -m pytest tests/ --co -q` no tiene errores

### T3: Validación (30 min)
- [ ] `python -m pytest tests/ce_son/ -v` — tests de order_store
- [ ] `python -m py_compile` en todos los archivos modificados
- [ ] `make lint` si ruff está disponible
- [ ] Verificar que no hay syntax errors

### T4: Docs Update (30 min)
- [ ] Actualizar CHANGELOG.md con fixes de test errors
- [ ] Guardar memoria en engram

### T5: Engram Save (30 min)
- [ ] Guardar resumen de sesión
- [ ] Guardar estado actual del MVP

---

## Success Criteria

- [ ] Git commit exitoso
- [ ] Git tag v1.0.0 creado
- [ ] Test collection errors = 0
- [ ] Todos los archivos compilan sin errores
- [ ] Memoria guardada en engram

---

## Blockers

- Ninguno identificado
