# SDD 0003: Hermes Agent Factory + Supervisor (arquitectura agent-native)

## Objetivo
Eliminar la creación manual de bots por cliente. Hermes recibe una ORDEN en lenguaje
natural, decide qué tipo de trabajo es y, si hace falta, materializa un agente OpenClaw
autónomo con su identidad, lo enlaza a un canal y lo opera 24/7.

## Arquitectura (cero bots hardcodeados por cliente)
```
Orden (CLI/Telegram/WhatsApp/web/voz)
        │
        ▼
┌── Hermes Supervisor ──┐   clasifica → pregunta | agente | ejecutar | enviar | asset
│  (hermes_supervisor.py)│
└──────┬────────────────┘
       ├─ pregunta → OKF/Engram → respuesta natural (cita fuente)
       ├─ agente   → Agent Factory → openclaw agents add (identidad + routing canal)
       ├─ ejecutar → delega a OpenCode (este agente: edita/deploya/automatiza)
       ├─ enviar   → openclaw agent / wacli (skill)
       └─ asset    → skill generación (fal-ai, comfyui, tts)
```

## Módulos
- `Orchestrator/hermes_agent_factory.py`:
  - LLM (deepseek-v4-flash) diseña identidad JSON {nombre, rol, directrices[], skill, canal}
  - Escribe `IDENTITY.md` + `AGENTS.md` en el workspace del agente
  - Registra con `openclaw agents add --non-interactive --workspace --model --bind <canal>`
- `Orchestrator/hermes_supervisor.py`:
  - Router LLM → clasifica la orden en uno de los 5 tipos
  - Ejecuta o delega según tipo

## Contrato de clasificación
Responde SOLO JSON: {tipo, tenant, razon, accion_propuesta}
- pregunta: dato/conocimiento (no toca archivos)
- agente: atender/vender/captar de forma autónoma → crear agente OpenClaw
- ejecutar: tocar código/archivos/deployar → OpenCode
- enviar: mandar msj/audio/archivo YA → skill
- crear_asset: generar imagen/voz/video → skill generación

## Prerequisito de infraestructura
- El gateway OpenClaw (`openclaw-gateway.service`) DEBE tener OPENROUTER_API_KEY en su
  entorno. Se carga vía `/tmp/sonora.env` (EnvironmentFile del service). Sin esto, los
  agentes OpenClaw mueren con "No API key for provider openrouter".

## Demostración verificada (caso César/Aztrotech)
- Factory creó agente `cesar` desde orden en español, enlazado a telegram.
- El agente responde: se presenta como asistente de César, NO revela SDC, NO da precios,
  captura lead (nombre, empresa, teléfono, necesidad, ubicación, horario) y deriva a César por WhatsApp.

## No-objetivos (por ahora)
- Auto-clonación de voz de César (XTTS) — siguiente iteración
- Dataset LoRA fotos — siguiente iteración
- UI de administración de agentes
