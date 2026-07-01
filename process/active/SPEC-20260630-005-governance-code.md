# SPEC — FASE 3: Governance as Code

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260630-005` |
| **Fecha** | 2026-06-30 |
| **Autor** | OpenClaw |
| **Tier** | 2 |
| **Estado** | activo |
| **Score requerido** | ≥60 |

---

## 1. Objetivo

Mover las reglas de gobernanza de documentos Markdown a la infraestructura de CI/CD de GitHub, para que ningún agente pueda saltarse las reglas aunque use `--no-verify`.

---

## 2. Value Driver

reliability, automation, founder-independence

---

## 3. Functional Requirements

| FR# | Descripción |
|-----|-------------|
| FR1 | `tests.yml`: lint falla en errores (sin `|| true`), coverage gate estricto (sin `2>/dev/null`) |
| FR2 | `process-gate.yml`: detectar tier desde el diff, exigir score ≥60 para tier 2+, fail en eventos |
| FR3 | Auto-assign workflow: cuando se crea un SPEC en PR, asigna reviewer automáticamente |
| FR4 | PR template con checklist de SPEC + README + tests |
| FR5 | Branch protection: PR required, 1 approval, status checks obligatorios |
| FR6 | CI corre en todos los pushes, no solo PRs |

---

## 4. Success Criteria

- [ ] `ruff check` falla el CI si hay errores (no más `|| true`)
- [ ] `pytest --cov-fail-under=60` falla el CI si cobertura baja de 60%
- [ ] PR sin SPEC activo es rechazado automáticamente
- [ ] PR template aparece al crear PR
- [ ] Branch protection bloquea push directo a main

---

## 5. Technical Approach

- Modificar YAMLs existentes (tests.yml, process-gate.yml, docker-build.yml)
- Crear `.github/PULL_REQUEST_TEMPLATE.md`
- Crear `.github/workflows/auto-assign.yml`
- Configurar branch protection via GitHub CLI (`gh api`)

---

## 6. Dependencies

- GitHub CLI (`gh`) instalado en CI runner ✅
- GITHUB_TOKEN con permisos de administración ✅
- GitHub branch protection API accesible ✅

---

## 7. Events to Emit

| Evento | Cuándo |
|--------|--------|
| `governance_hardened` | CI gates actualizados |
| `branch_protection_enabled` | Branch protection configurado |

---

## 8. Kill Criteria

Si los gates son tan estrictos que bloquean cambios legítimos de infraestructura, agregar excepción para `infra/` y `process/` paths.

---

## 9. Scale Criteria

Cuando haya >5 repos, centralizar los gates en una GitHub Action reutilizable.
