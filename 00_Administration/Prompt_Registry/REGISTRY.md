# SDC Prompt Registry — ÍNDICE MAESTRO

**Regla:** ningún prompt de creación se usa sin aprobar el **Spec Judge** (PASS + score >= 80).

## Prompts registrados

| id | versión | estado | score judge | veredicto | fecha | notas |
|---|---|---|---|---|---|---|
| `cinematic_hyperreal` | v1.0.0 | **approved** | 94.0 | PASS | 2026-08-13 | imagen/video cinematográfico FLUX/SD + control de guion |
| `brand_voice` | v1.0.0 | **approved** | 91.0 | PASS | 2026-08-13 | voz/tono de marca personal + colores + filosofía |
| `content_free` | v1.1.0 | **approved** | 96.0 | PASS | 2026-08-22 | motor contenido 100% libre, neutral, anti-gasto (SDD 0011) |

## Historial de evaluaciones

| fecha | prompt | veredicto | score | min | detalle |
|---|---|---|---|---|---|
| 2026-08-13 | cinematic_hyperreal v1.0.0 | PASS | 94.0 | 80 | cumple CA1-CA6, coverage Gherkin, costo<=$0.50 |
| 2026-08-13 | (prueba negativa, prompt malo) | FAIL | 0.0 | 80 | omitió directivas, texto en imagen, sin contexto — rechazado ✓ |
| 2026-08-13 | brand_voice v1.0.0 | PASS | 91.0 | 80 | voz de marca, paleta, filosofía, anti-guiones — aprobado ✓ |
| 2026-08-22 | content_free v1.0.0 | FAIL | 59.0 | 80 | omitió ACs, assets manuales, feedback_loop, topes — mejorado ✓ |
| 2026-08-22 | content_free v1.1.0 | PASS | 96.0 | 80 | cubre AC1-AC6, Gherkin 1-3, $0 libre, neutral — aprobado ✓ |

## Cómo registrar un nuevo prompt
1. Crear `prompts/<id>/` con spec → features (Gherkin/BDD) → PROMPT.md.
2. Escribir los tests PRIMERO (TDD) en `features/`.
3. Generar evals en `evals/` y evidencia en `assets/`.
4. Correr `scripts/spec_judge.py` — solo pasar a `approved` si PASS >= 80.
5. Agregar fila aquí. Unificar si existe un prompt equivalente (eliminar redundancia).
