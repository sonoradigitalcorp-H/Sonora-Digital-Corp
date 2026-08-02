---
type: decision
title: "Backend IA: FAL.ai"
status: active
tags: [decision, architecture, clone]
created: 2026-07-18
---

# Backend IA: FAL.ai (no GPU local)

**Contexto**: No hay GPU en el VPS. Se necesita entrenamiento LoRA + generación de imágenes/video.

**Decisión**: Usar FAL.ai para todo el procesamiento GPU. FAL_API_KEY ya configurado.

**Alternativas**: GPU propia (RunPod ~$30/mes), FaceFusion local (requiere GPU).

**Consecuencia**: Dependencia externa, pero sin inversión en hardware. Costo ~$5-6/cliente.
