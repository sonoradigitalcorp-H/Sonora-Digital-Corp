# Mapeo de Modelos por Actividad — OpenClaw / SDC

> Estado: DOCUMENTADO, pendiente de aplicar. No se tocó openclaw.json (agentes vivos).
> Backup: `~/.openclaw/openclaw.json.bak-ollama-20260808-074531`
> Ollama VPS: `http://149.56.46.173:11434` (docker, CPU, 11GB RAM, gratis, ilimitado)

## Principio
- Ollama VPS = trabajo pesado/corto/masivo (gratis, sin límites)
- OpenRouter = solo razonamiento premium CUANDO haya créditos (key $0 hoy)
- NUNCA modelos locales de difusión en el VPS (CPU-only → inútil)

## Modelos disponibles en Ollama VPS
| Modelo | Tamaño | Uso | Capabilities |
|---|---|---|---|
| qwen2.5:3b | 1.9GB | Chat/fast/automejora/clasificación | completion, tools |
| qwen2.5vl:3b | 3.2GB | Visión (analizar imágenes/frames) | vision, completion |
| nomic-embed-text | 274MB | Embeddings (768-dim, mejor calidad) | embedding |
| all-minilm | 45MB | Embeddings (384-dim, rápido/barato) | embedding |

## Mapeo por actividad

| Actividad | Modelo | Vía | Costo |
|---|---|---|---|
| Chats bot simples (cesar/rye) | qwen2.5:3b | Ollama VPS | $0 |
| Clasificación de lead | qwen2.5:3b | Ollama VPS (router.py fallback) | $0 |
| Embeddings RAG/Engram | all-minilm o nomic-embed | Ollama VPS | $0 |
| Auto-mejora nocturna (5:30 AM) | qwen2.5:3b | autonomous_loop.py + call_llm fallback | $0 |
| Análisis de imágenes | qwen2.5vl:3b | Ollama VPS /v1 | $0 |
| Análisis de video | qwen2.5vl:3b + ffmpeg frames | Ollama VPS | $0 |
| Resúmenes CRM (audio report) | qwen2.5:3b | crm_api.py (Ollama→OpenRouter→heurístico) | $0 |
| Razonamiento premium (estrategia) | deepseek-v4-flash-0731 | OpenRouter SOLO con créditos | ~$0.14/M |
| Crear imágenes | fal-ai/FLUX (lead_demo.py) | API pagada (FAL_KEY) | pago |
| Crear video | runway/fal-ai | API pagada | pago |

## Cómo aplicar a OpenClaw (cuando decidas)
OpenClaw soporta providers configurables (`agents.defaults.model.primary` + `agents.list[].model`).

1. Registrar provider Ollama en openclaw.json:
   ```json
   "providers": {
     "ollama": { "baseUrl": "http://149.56.46.173:11434/v1" }
   }
   ```
2. `agents.defaults.model.primary` → `ollama/qwen2.5:3b`
3. Agentes ventas que requieran más calidad → mantener `openrouter/deepseek/deepseek-v4-flash-0731` (fallback por key) o `ollama/qwen2.5:3b` según caso.
4. Backup ANTES de editar. Reiniciar gateway y esperar 10-15s.

## Notas
- Modelos `:free` de OpenRouter existen (14) pero rate-limited diario (429) — no confiables.
- El mayor gasto de tokens es OpenClaw (4 agentes) — al conectar a Ollama se elimina.
- ffmpeg local está ROTO (libva symbol error). Usar PIL para resize, no ffmpeg.
