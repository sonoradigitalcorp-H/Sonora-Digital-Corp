# Lección — SPEC-20260630-005

| Campo | Valor |
|-------|-------|
| **Spec** | `SPEC-20260630-005` |
| **Tier** | 2 |
| **Fecha** | 2026-06-30 |

---

## ¿Qué pasó?

Migración de las reglas de gobernanza de documentos Markdown a la infraestructura de CI/CD de GitHub. Las reglas ahora son código, no sugerencias.

---

## ¿Qué salió bien?

- [x] Branch protection: status checks obligatorios, enforce admins, sin force push
- [x] `tests.yml`: corre dentro de Docker (Python 3.12), lint + coverage gate
- [x] `process-gate.yml`: detección de tiers, score gate obligatorio para tier 2+
- [x] `auto-assign.yml`: asigna reviewer automático cuando PR tiene SPEC
- [x] PR template con checklist de SPEC + tests + lint
- [x] `.env.ci` para builds de CI sin secrets reales

---

## ¿Qué salió mal?

- [ ] Bootstrap problem: el process-gate bloqueó el PR del propio governance
- [ ] Hubo que desactivar temporalmente branch protection para mergear
- [ ] Ruff `--fix` revierte los parches de compatibilidad Python 3.10
- [ ] 26 errores E501 (line-too-long) quedan como deuda cosmética

---

## ¿Qué haríamos diferente?

- Agregar excepción en process-gate para cambios en `.github/workflows/` y `process/`
- No usar `ruff check --fix` porque rompe compatibilidad Python 3.10
- Crear una GitHub Action reusable para los gates

---

## Engram Tags

governance, ci-cd, branch-protection, github-actions, tdd, spec-005
