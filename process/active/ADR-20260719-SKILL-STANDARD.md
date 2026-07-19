# ADR — Skill Standardization Pipeline

| Campo | Valor |
|-------|-------|
| **ID** | `ADR-20260719-SKILL-STANDARD` |
| **Fecha** | 2026-07-19 |
| **Spec** | SPEC-20260719-UNIFICACION (FR-01, FR-02, FR-03, FR-07) |
| **Estado** | activo |

## Contexto
Existen skills en 4 formatos distintos: SDC template (14 campos), SDC simplified (6 campos), JSON (Hermes Telegram), y plugin binaries (OpenClaw). No hay validación automatizada de que las skills cumplan el estándar. Las skills skeleton tienen herramientas definidas pero les falta estructura completa.

## Decisión
1. **Pipeline de estandarización**: Toda skill nueva o existente debe pasar por: Research→Spec→BDD→TDD→Implement→Verify
2. **Checklist automatizado**: Script que valida los 14 campos del SKILL-TEMPLATE.md
3. **Skill Registry index**: `skills/INDEX.md` con lista de todas las skills, su estado (completo/skeleton/migrando)
4. **Skill evals**: Tests en evals/ que verifican skills completas

## Opciones Consideradas
| Opción | Pros | Contras |
|--------|------|---------|
| **Pipeline formal + checklist (elegido)** | Calidad garantizada, evitable | Más overhead por skill |
| Solo checklist sin tests | Rápido | No automatizable |
| Sin estandarización | Cero trabajo | Skills inconsistentes para siempre |

## Consecuencias
- Positivas: Skills production-ready con recovery procedures
- Positivas: Evals detectan skills incompletas automáticamente
- Trabajo: ~28 skills a migrar/completar

## Lecciones
- El template de 14 campos es extenso pero cada campo tiene propósito
- Las skills skeleton existentes ya tienen tools y descripción — el trabajo es agregar los 8 campos faltantes
