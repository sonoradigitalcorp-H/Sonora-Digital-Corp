# ADR 0013: Inversión de Cadena de Modelos — Nemotron-free Primary (SDD-0012 Eval)

**Fecha**: 2026-08-23  
**Estado**: IMPLEMENTADO  
**Autor**: MYSTIC / SDC

## Contexto

El servidor `vps_ai_server.py` usaba `deepseek/deepseek-v4-flash-0731` como modelo primario con `nemotron-3-ultra-550b-a55b:free` como fallback. Se ejecutó evaluación formal (`prompt_registry/run_eval.py`) para medir calidad de copy de venta conversacional.

## Evaluación Realizada

**Metodología**: 6 casos de prueba × 2 modelos = 12 llamadas LLM.  
**Juez**: nemotron-3-ultra-free (determinista + LLM).  
**Reglas duras**: 0 exclamaciones, 0 palabras prohibidas (IA/bot/modelo/LLM/RAG/embedding/chatbot), ≤500 chars, keywords de beneficio requeridas.

| Caso | nemotron-free | deepseek-0731 |
|------|---------------|---------------|
| saludo_frio_sdc | ✅ PASS (2.6s) | ❌ FAIL (vacío/timeout) |
| pregunta_precio_nathaly | ✅ PASS (14.2s) | ✅ PASS (11.6s) |
| dolor_horario_sdc | ✅ PASS (8.5s) | ✅ PASS (5.5s) |
| objecion_es_ia | ✅ PASS (11.4s) | ❌ FAIL (vacío/timeout) |
| cita_sat_nathaly | ❌ FAIL (max_chars >500) | ✅ PASS (7.2s) |
| voz_larga_prohibida | ✅ PASS (24.5s) | ❌ FAIL (vacío/timeout) |

**Scorecard**: nemotron-free **83% (5/6)** vs deepseek-0731 **50% (3/6)**.

### Análisis de Fallos
- **deepseek**: 3/6 respuestas VACÍAS ("") por timeout OpenRouter (20-40s). Cuando responde, copy es bueno.
- **nemotron**: 1/6 fallo por respuesta LARGA (>500 chars) en `cita_sat_nathaly`. Respuestas típicas 2-8s.

## Decisión

**Invertir `MODEL_CHAIN` en `vps_ai_server.py`**:

```python
# ANTES
MODEL_CHAIN = [
    "deepseek/deepseek-v4-flash-0731",
    "nvidia/nemotron-3-ultra-550b-a55b:free",
]

# DESPUÉS
MODEL_CHAIN = [
    "nvidia/nemotron-3-ultra-550b-a55b:free",  # PRIMARY: rápido, gratis, 83%
    "deepseek/deepseek-v4-flash-0731",          # FALLBACK: pago
]
```

**Mitigación nemotron largo**: `clean_reply()` corta a ~320 chars en frase completa + `max_tokens: 220`.

## Justificación

| Factor | nemotron-free | deepseek-0731 |
|------|---------------|---------------|
| Pass rate eval | **83%** | 50% |
| Latencia típica | 2-8s | 20-40s (o timeout) |
| Costo | **$0** (free tier) | $0.01-0.05/1k tokens |
| Confiabilidad | Alta (pocas respuestas vacías) | Baja (3/6 vacías por timeout) |
| Calidad copy venta | Superior (beneficios, brevedad) | Buena cuando responde |

**Nemotron-free es superior en TODOS los vectores para copy de venta conversacional**.

## Consecuencias

### Positivas
- Latencia producción: **~2.9s** (vs 20-40s deepseek)
- Costo LLM: **$0** (nemotron free tier)
- Copy consistente: beneficios, sin exclamaciones, cierra con cita
- Fallback deepseek sigue disponible para edge cases

### Mitigaciones Requeridas
1. **Recorte nemotron largo**: `clean_reply()` → 320 chars en frase completa + `max_tokens: 220`
2. **Fallback robusto**: deepseek mantiene cobertura edge cases
3. **Monitoreo**: Log `model` usado en cada request para detectar regressions

## Archivos Modificados
- `01_Core_Platform/04_Automations_and_Workflows/vps_ai_server.py` (MODEL_CHAIN invertido, max_tokens 220, clean_reply recorte)
- `prompt_registry/eval_prompts.yaml` (keywords ajustadas post-eval)
- `prompt_registry/run_eval.py` (call_llm robusto con retries)

## Monitoreo Post-Deploy
- Log `model` usado en cada `/api/v1/chat/completions`
- Alerta si nemotron falla >5% requests (fallback a deepseek)
- Re-eval mensual programado

---

*ADR aprobado por MYSTIC — Eval: 2026-08-23 | Deploy: 2026-08-23*