# Leccion — SPEC-20260703-003

| Campo | Valor |
|-------|-------|
| **Spec** | `SPEC-20260703-003` |
| **Tier** | 2 |
| **Fecha** | 2026-07-03 |

---

## Que paso?

Se documento toda la sesion anterior (Hermes Asteroid + Unified Brain v2) segun la metodologia de proceso (CONDUCT.md), y se creo un sistema auto-doc que genera automaticamente SPEC.md, SCORE.md, ADR.md, LECCION.md, events.jsonl y gherkin desde el resumen de sesion en AGENTS.md.

---

## Que salio bien?

- [x] FASE 1 completa: 12 archivos de proceso creados para 2 iniciativas
- [x] CATALOG.md limpiado de placeholders rotos
- [x] FASE 2 completa: auto-doc.py funciona con --auto y modo manual
- [x] Agent process-doc registrado en opencode.json
- [x] CONDUCT.md actualizado con checklist de cierre de sesion
- [x] AGENTS.md actualizado con instrucciones de compliance
- [x] /doc command registrado

---

## Que salio mal?

- [x] auto-doc.py tuvo 3 iteraciones de bugs (f-string backslash, format key errors, sintaxis Python <3.12)
- [x] El hermes-asteroid entry en CATALOG.md se perdio accidentalmente al limpiar entries de prueba
- [x] --auto mode genero spec duplicada en CATALOG.md que requirio limpieza manual

---

## Que hariamos diferente?

- No usar f-strings con backslashes (incompatible Python <3.12)
- Probar auto-doc con --dry-run antes de generar archivos reales
- Usar --dir explicito en lugar de auto-generar desde spec-id
- Escribir tests para auto-doc.py antes de considerarlo listo

---

## Engram Tags

auto-doc, process, documentation, compliance, methodology, spec, adr, leccion, score, gherkin
