# ADR 0002: Unificación de fuentes de verdad + modelo LLM para bots Telegram

## Contexto
El 2026-08-08/09 se cambió el modelo de los 4 agentes OpenClaw de
`openrouter/deepseek/deepseek-v4-flash-0731` a `ollama/qwen3:4b` (VPS OVH)
buscando costo $0. Resultado: los bots de Telegram quedaron "mudos" y
mostraban su proceso de razonamiento en el chat.

## Díagnóstico (qué NO funcionaba)
1. **qwen3:4b con capability `thinking`**: consume todo el presupuesto de
   tokens en razonamiento interno (`done_reason=length`) y devuelve
   `content: ''` vacío. Verificado 3 veces con num_predict 10/40/200.
   Sintoma visible: "el bot de César lanza su proceso de pensamiento".
2. **Tres fuentes de verdad contradictorias**: ESTADO.md, INBOX/PROTOCOLO.md
   y openclaw.json decían modelos/keys distintas (ollama local vs VPS vs
   openrouter; key 282...732 expirada vs 934c2fa...).
3. **Gateways duplicados**: 2 procesos OpenClaw (uno huérfano PPID=1)
   compitiendo por el puerto 18789 → sesiones partidas.
4. **Ollama local sin qwen3:4b**: solo all-minilm (embeddings). El INBOX
   afirmaba "qwen3:4b local 127.0.0.1" = falso.

## Decisión
1. **Modelo LLM de agentes vuelve a** `openrouter/deepseek/deepseek-v4-flash-0731`
   (verificado en vivo: responde `content` correcto; el campo `reasoning` es
   adicional, no rompe nada). Key activa: `sk-or-v1-934c2fa...` (limit 10, uso 2.3).
2. **Ollama queda SOLO para**: embeddings RAG (all-minilm local 127.0.0.1 +
   VPS 149.56.46.173) y como fallback $0 (`qwen2.5:3b`, SIN thinking) si
   OpenRouter se queda sin saldo.
3. **Verdad única**: ESTADO.md e INBOX corregidos; openclaw.json es la fuente
   runtime. Regla: antes de tocar, `git log --oneline -1` + `git status --short`.
4. **Un solo gateway**: PID systemd canónico en puerto 18789; memory-guard
   mata duplicados (RAM<400MB).

## Voz (modo demo César)
- TTS edge-tts `es-MX-DaliaNeural` (Telegram) / `es-MX-JorgeNeural` (WhatsApp).
- **Limpieza obligatoria antes de sintetizar**: quitar emojis, signos de
   admiración (¡!), asteriscos/markdown y cualquier texto de razonamiento.
- **Sin pitching**: respuestas orientadas a ayudar/demostrar capacidad, no a
   vender agresivamente.

## Estado
Aceptado (2026-08-10). Verificado: gateway único, bots responden con voz,
deepseek responde content, key activa.

## Enlaces
- Engram obs 580 (bug qwen3 content vacío), obs 581 (unificación completa)
- `ESTADO.md` L5/L9/L20, `INBOX/PROTOCOLO.md`
- `~/.openclaw/openclaw.json` + backup `bak-unificado-*`