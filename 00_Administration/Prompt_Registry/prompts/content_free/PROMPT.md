# content_free — Motor de Contenido 100% Libre (Neutral + Mejorable)

Prompt canónico versionado para el pipeline `sdc-content-free`.
Versión: v1.1.0 — 2026-08-22 (revisado tras SPEC JUDGE FAIL→mejora)

## Identidad (NEUTRAL)
Este motor NO está atado a Sonora Digital Corp. El nicho, CTA, voz y hashtags
se inyectan por `config.json` (config.py). Mismos módulos sirven para cualquier
cliente PyME. Cero hardcode de marca en los scripts.

## Proveedores libres (lista blanca — cost_gate.py)
`hf-zerogpu` · `edge-tts` · `ffmpeg` · `composio` · `nemotron-free` · `gemini-free`
Cualquier proveedor fuera de esta lista → bloqueado con FREE_TIER_ONLY=true.

## Criterios de aceptación cubiertos (mapeo a spec SPEC.md AC1-AC6)
- AC1 Puerta anti-gasto: `cost_gate.gate(provider)` se llama antes de TODA petición
  externa. Proveedor fuera de lista blanca → `GateRejected`.
- AC2 Pipeline end-to-end (guion→imagen→voz→video→publicar) produce MP4 9:16 y
  publica en IG sin error. También soporta **activos manuales**: si el Jefe pasa
  imagen/audio propios, el pipeline omite generadores de IA y solo compone+publica.
- AC3 Imagen vía HF ZeroGPU (FLUX.1-dev / Z-Image-Turbo) devuelve URL descargable;
  token `canPay:false` verificado → $0.
- AC4 SPEC JUDGE score ≥ 80 → estado `approved` en REGISTRY.md (este archivo).
- AC5 `feedback_loop.py` escribe métricas IG (likes/reach/views) y ajusta
  `peso_template` en JSON persistente (`logs/feedback.json`), trazable en log.
- AC6 `pytest tests/` pasa (unit + e2e); integrity grep = 0 refs veo/seedance/fal.

## Costo (cost_compliance)
- Modo libre (default): costo por operación = **$0.00**. Tope duro $0.
- Modo pagado (ALLOW_PAID=true, requiere OK Jefe): tope APPROVED_BUDGET=$0.50,
  cada gasto se loguea en `logs/cost.log`. Sin OK → nada de pago se ejecuta.
- No usa num_frames/num_images (no genera video por difusión; usa imagen estática
  + voz). Si algún día se añade video por difusión: num_frames<=64, num_images<=1.

## Reglas de composición (platform_fit IG 9:16)
- Resolución 1080x1920 (9:16). Subtítulo quemado vía filtro `subtitles` (libass),
  color dorado #C9A227, fuente 48px, alineado inferior.
- Voz `es-MX-DaliaNeural` (edge-tts, $0). CTA del config (default wa.me).
- Máx 3 assets/día sin OK explícito.

## Estructura del guion (canónica, neutral)
[HOOK 3s] provocación + nicho
[PROBLEMA] dolor concreto del negocio
[SOLUCIÓN] IA como "cerebro con superpoderes"
[PRUEBA] antes/después o cifra
[CTA] único, del config

## Escenarios Gherkin cubiertos (features/pipeline.feature)
1. Genera reel con imagen HF + voz edge-tts → MP4 9:16 → publica IG → costo 0.
2. Acepta activos manuales → compone+publica → NO llama generadores de IA.
3. feedback_loop ajusta pesos tras métricas → JSON persistente + log.

## Trazabilidad
spec → features → TDD → evals → SPEC JUDGE → REGISTRY.md. Todo en
`Prompt_Registry/prompts/content_free/`.
