# Costos y Comparativa de Modelos — Call Engine

## Gasto Real Actual (OpenRouter)

| Métrica | Valor |
|---------|-------|
| Total gastado | **$0.21 USD** |
| Período | Julio 2026 (free tier) |
| Saldo restante | **$0.00** (no compró créditos) |
| Límite free tier | 429 req/día por modelo |

**Equivalente en MXN**: $0.21 USD × ~18 = **$3.78 MXN** (todo el mes)

---

## Comparativa de Modelos

### API Externa (OpenRouter / OpenCode)

| Modelo | $/1M tok in | $/1M tok out | Costo por llamada típica | Calidad |
|--------|:----------:|:-----------:|:----------------------:|:-------:|
| **Gemma 4 26B** (OR free) | **$0.00** | **$0.00** | **$0.00** | ⭐⭐⭐ |
| **DeepSeek V4 Flash** (OpenCode) | **$0.00** | **$0.00** | **$0.00** | ⭐⭐⭐⭐ |
| **Llama 3.2 3B** (OR free) | **$0.00** | **$0.00** | **$0.00** | ⭐⭐ |
| **Mistral Nemo** (OR free) | **$0.00** | **$0.00** | **$0.00** | ⭐⭐⭐ |
| **GPT-4o-mini** (OR pago) | $0.15 | $0.60 | **$0.0003** | ⭐⭐⭐⭐⭐ |
| **DeepSeek V3** (OR pago) | $0.10 | $0.40 | **$0.0002** | ⭐⭐⭐⭐⭐ |

### Local (Ollama en VPS OVH, CPU-only)

| Modelo | Tamaño | RAM | TPS real | Costo | Tiempo 50 tok |
|--------|:-----:|:---:|:--------:|:-----:|:------------:|
| **tinyllama:1.1b** | 637MB | 0.8GB | **3 tok/s** | $0 | **16.7s** |
| **llama3.2:3b** | 2.0GB | 2.5GB | **2 tok/s** | $0 | **25s** |
| **qwen2.5:3b** | 1.9GB | 2.5GB | ~2 tok/s | $0 | ~25s |
| **gemma:2b** (cuantizado) | 1.3GB | 1.5GB | ~4 tok/s | $0 | ~12s |

### Modelos Recomendados para Integrar

| Modelo | Dónde | Por qué |
|--------|-------|---------|
| **DeepSeek V4 Flash** | OpenCode Go (¡gratis!) | Ya tienes API key, es rápido, calidad alta |
| **Gemma 4 26B** | OpenRouter free | Gratis, 26B parámetros, calidad excelente |
| **Mistral Nemo** | OpenRouter free | Gratis, 12B params, rápido para su tamaño |
| **tinyllama:1.1b** | Ollama local | Rápido localmente, para tests unitarios |
| **GPT-4o-mini** | OpenRouter pago | $0.0003/llamada — calidad máxima |

---

## Recomendación Final

| Escenario | Modelo | Costo/día (1000 llamadas) |
|-----------|--------|:------------------------:|
| 🏆 Producción call engine | **DeepSeek V4 Flash** (OpenCode) | **$0.00** |
| 🏆 Producción call engine | **Gemma 4 26B** (OR free) | **$0.00** |
| ⚡ Rápido + calidad | **GPT-4o-mini** (OR pago) | **$0.30 USD ≈ $5.40 MXN** |
| 🧪 Tests locales | **tinyllama:1.1b** (Ollama) | **$0.00** |
| 🧪 Eval de prompts | **Gemma 4 26B** (OR free, con créditos) | **$0.00** (si tienes ≥$10 de crédito) |

> **Nota**: OpenRouter free tier requiere ≥$10 de crédito para desbloquear 1000 req/día gratis. Sin crédito, límite de 429 req/día por modelo que ya alcanzaste hoy.

### Próximo paso recomendado

**Agregar $10 USD (~$180 MXN) a OpenRouter** → desbloquea modelos gratis ilimitados (Gemma 4 26B, Mistral Nemo, etc.) y acceso a GPT-4o-mini a $0.0003/llamada.
