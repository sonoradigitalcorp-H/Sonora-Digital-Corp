# SESSION — 2026-08-03 · Asistente de IA para Alex (RYE)

## Executive Summary

Se construyó y entregó a Alex Usa (12059021830, Shift Manager de Producción en RYE) una propuesta completa
de asistente de IA por Telegram construido con OpenClaw + Sonora Digital Corp. La entrega incluyó nota de voz,
presentación formal PDF + 13 slides, mockups del chat en acción, diagrama de arquitectura MCP y un video demo
del asistente resolviendo un turno de producción completo. Se documentó el pipeline de audio correcto
(edge-tts → resample 16k → OGG/Opus) y se resolvió la entrega de video a WhatsApp (webm rechazado → mp4 h264
con ffmpeg estático).

---

## Contexto del cliente

- **Alex Usa** — `12059021830` (EE.UU., área 205 Alabama). Hermano del usuario.
- **Rol**: Shift Manager de Producción.
- **Empresa**: RYE Design (Claremore, OK) — integrador boutique de robótica. Fanuc, Cognex vision,
  Lincoln automation, Servo-Robot, Yaskawa. Líneas: ensamble complejo, material handling, machine vision,
  machine tending, soldadura. Programan líneas para BMW, Rivian, VW y Mercedes.
- **Situación previa**: el hermano (Perroni) programa robots para RYE; trabajan con peleceros/fleteros y
  procesos manuales; hay sistema pero no inteligente. Alex pidió el proyecto de SDC (2026-08-03).

## Propuesta entregada (8 casos de uso)

1. **Shift report automático** al cerrar cada turno (unidades, paros, motivos, calidad).
2. **Control de personal** — retardos, ausencias, cobertura antes del arranque.
3. **Minutas de juntas** — audio → acuerdos con responsables y fechas.
4. **Dashboard OEE en tiempo real** por línea + causa raíz de cada paro.
5. **Mantenimiento predictivo de robots Fanuc** — alerta antes de que truene.
6. **Verificación proactiva de procesos** — desviaciones antes de que salga pieza mala.
7. **Coordinación de fleteros/docks** — trailers, docks, pendientes de carga/descarga.
8. **Reportes automáticos para clientes** — BMW, Rivian, VW, Mercedes con gráficas.

## Datos de industria usados en la propuesta

- Downtime en línea automotriz: **$1.3M–2.3M USD por hora**.
- Mantenimiento predictivo: **250–300% ROI**, reduce downtime no planeado 30–50%, costos 25–40%.
- Caso real: OEE **67% → 82% en 90 días**, -47% downtime.
- Inspección visual IA: **99.8% precisión**.
- 40% de los incidentes nacen en el cambio de turno → handover digital = 34% menos incidentes.

## Arquitectura propuesta (cómo funciona SDC)

- **6 capas concéntricas**: kernel (identidad), infra, apps (core), products, tenants (clientes), portal.
- **Validación**: SDD → BDD (Gherkin) → ADR → quality gate → CI/CD. 852 tests.
- **Infra**: PostgreSQL 15, Redis, Qdrant (RAG), n8n, Hermes Gateway, Docker, edge-tts + whisper.
- **MCP**: estándar que conecta las herramientas de RYE al asistente en tiempo real —
  `fanuc-mcp`, `erp-mcp`, `cmms-mcp`, `hr-mcp`, `logistics-mcp`, `vision-mcp` (Cognex).
- **Agentes por área**: producción, mantenimiento, calidad, logística, RRHH, reportes.
- **Hoja de ruta**: Fase 1 (1 semana, piloto shift report + personal) → Fase 2 (30 días, MCP + OEE real) →
  Fase 3 (90 días, predictivo + agentes completos).

---

## Entregables y estado de envío

| Entregable | Archivo | Estado |
|------------|---------|--------|
| Nota de voz (8 casos de uso) | `scripts/voice_msg_alex_ai.py` | ✅ Enviada |
| Presentación PDF (13 páginas) | `scripts/send_alex_ai_deck.py` → `alex_ai_deck.html` | ✅ Enviada |
| 13 slides PNG | `scripts/send_alex_ai_deck.py` | ✅ Enviadas |
| Mockups chat (4 capturas) | `scripts/alex_chat_mockups.html` | ✅ Enviados |
| Diagrama MCP | `scripts/alex_mcp_diagram.html` | ✅ Enviado |
| Video demo (57.9s) | `scripts/alex_chat_video.html` → mp4 h264 | ✅ Enviado (ID 3EB09F2867077BB45E03C7) |
| Nota de voz + 7 slides (análisis financiero previo) | `scripts/voice_msg_alex.py`, `scripts/alex_deck.html` | ✅ Enviados |

### Fix crítico: video a WhatsApp

- Playwright graba `.webm` (VP8). **WhatsApp rechazó el webm** → el usuario confirmó que ningún video llegaba.
- **Solución**: ffmpeg estático (johnvansickle, v7.0.2) descargado a `/tmp/opencode/ffmpeg-7.0.2-amd64-static/`
  → `-c:v libx264 -pix_fmt yuv420p -movflags +faststart -c:a aac` → `demo_asistente_alex.mp4` (648KB).
- Enviado con `wacli send file --mime video/mp4` → **sent: true** (ID `3EB09F2867077BB45E03C7`).

### Fix crítico: pipeline de audio (sesiones previas, consolidado hoy)

- **Bug**: edge-tts produce MP3 a 24kHz; escribirlo como OGG declarando 16kHz sin re-muestrear → audio 1.5x
  lento y distorsionado.
- **Fix** (en `scripts/voice_note.py`): edge-tts → MP3 → soundfile (conserva sr real) → sox `-r 16000 -c 1`
  → soundfile OGG/OPUS → `wacli send voice`.
- **ffmpeg del sistema roto** (libva: `undefined symbol: va_fool_postp`) → se usa sox/soundfile y ffmpeg estático.
- **Voz**: `es-MX-DaliaNeural` (edge-tts).

---

## Archivos creados esta sesión

- `scripts/voice_note.py` — helper pipeline de audio correcto (`make_voice_note`).
- `scripts/voice_msg_alex_ai.py` — nota de voz de la propuesta (8 casos de uso).
- `scripts/send_alex_ai_deck.py` — renderiza y envía PDF + 13 slides.
- `scripts/alex_ai_deck.html` — presentación formal de 13 páginas.
- `scripts/alex_chat_mockups.html` — 4 mockups tipo WhatsApp del chat del asistente.
- `scripts/alex_chat_video.html` — animación del chat para el video demo.
- `scripts/alex_mcp_diagram.html` — diagrama de arquitectura MCP.
- `scripts/voice_msg_alex.py` — envío de análisis financiero previo (nota + 7 slides).
- `scripts/alex_deck.html` — deck de 7 slides del análisis financiero.
- `scripts/voice_msg_sergio.py` — refactorizado para usar `voice_note.py` (pipeline correcto).

## Notas operativas

- Store wacli autenticado: `~/.wacli/accounts/personal` (linked `5216623538272`).
- Contacto: `12059021830@s.whatsapp.net`.
- Artifacts renderizados (no versionados): `/tmp/opencode/alex_deck/`, `/tmp/opencode/alex_ai_render/`,
  `/tmp/opencode/alex_mockups/`, `/tmp/opencode/alex_mcp/`, `/tmp/opencode/alex_video/`.
