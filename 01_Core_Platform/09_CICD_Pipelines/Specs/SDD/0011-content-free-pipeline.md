# SDD 0011 — sdc-content-free: Motor de Contenido 100% Libre, Neutral y Mejorable

**Fecha:** 2026-08-22
**Autor:** COSUDE (OpenCode) bajo orquestación Hermes
**Estado:** DRAFT → TEST → APPROVED

## 1. Contexto y Problema

El `sdc-ai-content-engine` usa FAL.ai (imagen $0.05, video $0.10-$0.30) con tope $0.50/op.
Hallazgos 2026-08-22:
- `FAL_KEY` expirada (401) → no genera imagen/video nuevos.
- Se detectó un cargo de **$6 USD con Veo 3 (Google)** que el Jefe NO autorizó → fuga de gasto fuera del stack.
- Veo 3 / Seedance (BYOK) NO son fiablemente gratis.

**Necesidad:** un motor de contenido que (a) sea 100% gratis por defecto, (b) sea **neutral** (adaptable a cualquier nicho/plantilla, no hardcodeado a SDC), (c) tenga **puerta anti-gasto** (ninguna API de pago corre sin OK explícito + tope), (d) sea **mejorable** vía feedback loop determinista.

## 2. Objetivo

Sistema `sdc-content-free` que produce post/reel IG end-to-end sin costo:
`guion (nemotron free)` → `imagen (HF ZeroGPU)` → `voz (edge-tts)` → `video (ffmpeg)` → `publicar (Composio IG)`.
Acepta también activos manuales del Jefe (imagen/video) y solo hace ffmpeg + publicar.

## 3. Principios de Diseño (neutral + mejorable)

- **Neutral:** nicho/secrets/prompts se inyectan por config, no por código. Mismos módulos sirven para cualquier cliente.
- **Libre por defecto:** `FREE_TIER_ONLY=true`. Lista blanca de proveedores: `hf-zerogpu`, `edge-tts`, `ffmpeg`, `composio`, `nemotron-free`, `gemini-free`.
- **Anti-gasto:** `cost_gate.py` bloquea cualquier llamada a proveedor fuera de la lista blanca; si `ALLOW_PAID=true` requiere `APPROVED_BUDGET` y log de cada gasto.
- **Mejorable:** `feedback_loop.py` registra métricas IG (likes/reach/views) y ajusta pesos de plantilla; evalúa con SPEC JUDGE periódico.
- **Trazable:** spec → Gherkin → TDD → evals → SPEC JUDGE, todo en `Prompt_Registry/prompts/content_free/`.

## 4. Componentes

| Módulo | Archivo | Proveedor | Costo |
|--------|---------|-----------|-------|
| Guion | `scripts/gen_script.py` | nemotron-free (OpenRouter) | $0 |
| Imagen | `scripts/gen_image.py` | HF ZeroGPU (FLUX.1-dev / Z-Image-Turbo) | $0 |
| Voz | `scripts/gen_voice.py` | edge-tts DaliaNeural | $0 |
| Video | `scripts/compose_video.py` | ffmpeg (wrapper) | $0 |
| Publicar | `scripts/publish_ig.py` | Composio INSTAGRAM_POST_IG_USER_MEDIA | $0 |
| Puerta | `scripts/cost_gate.py` | local | $0 |
| Loop | `scripts/feedback_loop.py` | Composio insights | $0 |
| Judge | `Prompt_Registry/scripts/spec_judge.py` (reusa) | deepseek-v4-flash-0731 | $0 |

## 5. Criterios de Aceptación (verificables)

1. `cost_gate` rechaza cualquier proveedor no en lista blanca cuando `FREE_TIER_ONLY=true`.
2. Pipeline end-to-end con activos manuales produce MP4 9:16 y lo publica en IG (sin error).
3. Generación de imagen vía HF ZeroGPU devuelve URL descargable (token `canPay:false` verificado).
4. SPEC JUDGE score ≥ 80 → estado `approved` en REGISTRY.md.
5. Feedback loop escribe métricas y ajusta `peso_template` en JSON persistente.
6. Tests unit + e2e pasan (pytest). Integrity: grep confirma cero refs a `veo`/`seedance`/`fal` en código libre.

## 6. Fuera de alcance

- Edición GUI OpenCut (pesada, no laptop 3.3GB) — manual opcional del Jefe.
- Video IA generado pagado (Veo/Seedance/FAL) — requiere OK + presupuesto.

## 7. Riesgos

- HF ZeroGPU cola compartida (30-120s) → pipeline usa background + poll.
- nemotron-free rate limit → fallback gemini-free-lite.
