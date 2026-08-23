# SPEC — content_free pipeline

## Objetivo
Producir post/reel IG end-to-end sin costo, neutral a cualquier nicho, con puerta
anti-gasto y loop de mejora.

## Público
PyMEs de Sonora (nicho inyectado por config). Plataforma: Instagram (9:16).

## Restricciones de costo
- FREE_TIER_ONLY=true. Tope por operación: $0.00 (solo lista blanca).
- Si ALLOW_PAID=true: APPROVED_BUDGET (default $0.50), log obligatorio.

## Criterios de aceptación (verificables)
AC1: cost_gate bloquea proveedor fuera de lista blanca con FREE_TIER_ONLY=true.
AC2: pipeline con activos manuales → MP4 9:16 publicado en IG sin error.
AC3: gen_image HF ZeroGPU → URL descargable (token canPay:false).
AC4: SPEC_JUDGE score >= 80 → estado approved en REGISTRY.md.
AC5: feedback_loop escribe métricas + ajusta peso_template (JSON persistente).
AC6: pytest unit + e2e pasan; integrity grep = 0 refs veo/seedance/fal.

## No-funcional
- Neutral: cero hardcode de nicho/marca en los módulos.
- Mejorable: feedback_loop ajusta pesos, re-evalúa con SPEC_JUDGE.
- Trazable: spec + features + evals + judge + assets en esta carpeta.
