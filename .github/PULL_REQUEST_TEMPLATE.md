## Descripción

<!-- Explica qué hace este PR -->

## SPEC

- [ ] Tier 1 (quick fix) — sin SPEC requerido
- [ ] Tier 2+ — SPEC en `process/active/SPEC-*.md`
- [ ] Score ≥60 (ver `process/active/SCORE.md`)

## Checklist

- [ ] Tests pasan: `pytest tests/unit/ -q`
- [ ] Cobertura ≥60%: `pytest --cov=src.core --cov-fail-under=60`
- [ ] Lint: `ruff check apps/ scripts/`
- [ ] README actualizado (si aplica)
- [ ] ADR documentado (si aplica)
- [ ] Eventos emitidos (si aplica)

## Breaking Changes

<!-- Marca si esto rompe algo existente -->

- [ ] No breaking changes
- [ ] Breaking changes (explicar abajo)
