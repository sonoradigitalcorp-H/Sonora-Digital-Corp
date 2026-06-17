# Feature Specification: Content Creation Pipeline

**Feature**: 019-content-pipeline
**Created**: 2026-06-10
**Status**: Active
**Input**: Pipeline completo de creación de contenido diario con IA.

---

## Objetivo

Crear contenido educativo, cursos y material multimedia de forma automatizada:
- Videos con fal.ai / ComfyUI
- Podcasts con TTS
- Artículos con LLM
- Tablas comparativas
- Audio personalizado
- Entrega multicanal (email, Telegram, WhatsApp, web)

---

## Stack Tecnológico

### 🎬 Video
| Herramienta | Tipo | Conexión | Puerto/Protocolo |
|------------|------|----------|-----------------|
| **Fal.ai** | Generación video/imagen | MCP via OpenClaw | HTTP → 18789 |
| **ComfyUI** | Generación imagen local | Docker (pendiente) | HTTP → 8188 |
| **Playwright** | Grabación pantalla | MCP via OpenClaw | npx playwright |
| **Video-frames** | Extracción frames | Skill OpenClaw | CLI |

### 🎙️ Audio
| Herramienta | Tipo | Conexión | Puerto/Protocolo |
|------------|------|----------|-----------------|
| **STT (Whisper)** | Voz → Texto | Local Hermes | localhost:8000 |
| **TTS (Edge)** | Texto → Voz | Hermes | edge-tts CLI |
| **sherpa-onnx** | TTS local | OpenClaw skill | CLI |
| **ElevenLabs** | TTS premium | API key | api.elevenlabs.io |

### 📝 Texto
| Herramienta | Tipo | Conexión | Puerto/Protocolo |
|------------|------|----------|-----------------|
| **DeepSeek V4** | LLM principal | OpenCode | opencode.ai |
| **Gemini** | LLM secundario | OpenClaw skill | api.google.com |
| **Engram** | Memoria/Contexto | SQLite+FTS5 | local |

### 🌐 Publicación
| Herramienta | Tipo | Conexión | Puerto/Protocolo |
|------------|------|----------|-----------------|
| **n8n** | Automatización | MCP | localhost:5679 |
| **Ghost CMS** | Blog/Sitio | OpenClaw skill | HTTP |
| **Brevo** | Email marketing | OpenClaw skill | API |
| **Telegram** | Mensajería | API Bot | api.telegram.org |
| **WhatsApp** | Mensajería | Bridge | localhost:3001 |

### 📊 Analytics
| Herramienta | Tipo | Conexión |
|------------|------|----------|
| **PostHog** | User analytics | OpenClaw skill |
| **Meta Ads** | Publicidad | OpenClaw skill |

---

## Pipeline Cuántico de Contenido

```
╔══════════════════════════════════════════════╗
║     OBSERVADOR (Tú) — Colapsa la realidad    ║
╚══════════════════════════════════════════════╝
                    ↓
         ╔══════════════════╗
         ║  INTENCIÓN       ║ ← "Quiero un video sobre X"
         ║  (Input)         ║
         ╚══════════════════╝
                    ↓
    ┌───────────┬───────────┬───────────┐
    ↓           ↓           ↓           ↓
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│ Research│ │ Script  │ │ Visual │ │ Audio  │
│ (LLM)  │ │ (LLM)   │ │ (Fal)  │ │ (TTS)  │
└────────┘ └────────┘ └────────┘ └────────┘
    ↓           ↓           ↓           ↓
    └───────────┴───────────┴───────────┘
                    ↓
         ╔══════════════════╗
         ║  SUPERPOSICIÓN   ║
         ║  (Edición/Armado)║
         ╚══════════════════╝
                    ↓
    ┌───────────┬───────────┬───────────┐
    ↓           ↓           ↓           ↓
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│ Video  │ │ Podcast│ │ Artículo│ │ Tabla  │
│ (MP4)  │ │ (MP3)  │ │ (HTML)  │ │ (CSV)  │
└────────┘ └────────┘ └────────┘ └────────┘
    ↓           ↓           ↓           ↓
    └───────────┴───────────┴───────────┘
                    ↓
         ╔══════════════════╗
         ║  ENTREGA         ║
         ║  (Multi-canal)   ║
         ╚══════════════════╝
                    ↓
    ┌───────┬───────┬───────┬───────┐
    ↓       ↓       ↓       ↓       ↓
  Email  Telegram  Web    WhatsApp  Blog
         ║
         ║  ↓
╔══════════════════════════════════════════╗
║  ENTANGLEMENT (n8n conecta todo)        ║
║  Cada acción afecta a todos los canales ║
╚══════════════════════════════════════════╝
```

---

## Conexiones Reales (MCP, APIs, Webhooks)

### n8n + GitHub Actions + MCP

```
GitHub Actions (trigger)
    ↓ push a main
n8n webhook (recibe)
    ↓ ejecuta workflow
OpenClaw → Fal.ai (genera video)
    ↓
JARVIS (guarda en Engram)
    ↓
Hermes → Telegram (notifica)
    ↓
Brevo → Email (entrega)
```

### Diagrama de Flujo Diario

```
6:00 AM — Cron job → Research Agent investiga tema
7:00 AM — LLM escribe guión
8:00 AM — Fal.ai genera imágenes/video
9:00 AM — TTS genera audio/podcast
10:00 AM — n8n arma contenido multicanal
10:30 AM — Entrega: Email + Telegram + Web
11:00 AM — PostHog registra analytics
```

---

## Herramientas Listadas

| # | Herramienta | Tipo | Estado | Para qué |
|---|------------|------|--------|----------|
| 1 | Fal.ai | Imagen/Video | ✅ Activo | Generar contenido visual |
| 2 | DeepSeek V4 | LLM | ✅ Activo | Escribir guiones, investigar |
| 3 | Whisper (STT) | Audio→Texto | ✅ Activo | Transcripción de voz |
| 4 | Edge-TTS | Texto→Audio | ✅ Activo | Podcasts, narración |
| 5 | n8n | Automation | ✅ Activo | Orquestar pipeline |
| 6 | Telegram | Messaging | ✅ Activo | Entregar contenido |
| 7 | WhatsApp | Messaging | ⚠️ QR pendiente | Entregar contenido |
| 8 | GitHub Actions | CI/CD | ✅ Activo | Deploy automático |
| 9 | Engram | Memory | ✅ Activo | Contexto persistente |
| 10 | PostHog | Analytics | ✅ Activo | Medir impacto |
| 11 | Ghost CMS | Blog | ✅ Activo | Publicar artículos |
| 12 | Brevo | Email | ✅ Activo | Email marketing |
| 13 | OpenClaw | Gateway | ✅ Activo | 52 skills |
| 14 | Hermes | Desktop/Voz | ✅ Activo | Interfaz de voz |
| 15 | Playwright | Browser | ✅ Activo | Automatización web |
| 16 | Meta Ads | Publicidad | ✅ Activo | Promocionar contenido |
| 17 | ComfyUI | Imagen local | ❌ Pendiente | Generación local |
| 18 | ElevenLabs | TTS premium | ⚠️ API key | Voz ultra realista |

---

## Plan de Implementación

### Phase 1: Pipeline Diario (Weeks 1-2)
- [ ] Crear n8n workflow "Daily Content Generator"
- [ ] Configurar cron para horarios de creación
- [ ] Integrar Fal.ai + TTS + LLM en pipeline

### Phase 2: Múltiples Formatos (Weeks 2-3)
- [ ] Video → Podcast automático (extraer audio)
- [ ] Artículo → Video resumen (fal.ai)
- [ ] Tablas → Infografías

### Phase 3: Entrega Multi-canal (Weeks 3-4)
- [ ] Email automático con Brevo
- [ ] Telegram broadcast
- [ ] WhatsApp broadcast (cuando QR esté listo)
- [ ] Blog en Ghost CMS

---

## Criterios de Éxito

- [ ] Pipeline diario generando contenido sin intervención
- [ ] 3+ formatos por contenido (video, podcast, artículo)
- [ ] Entrega multicanal automática
- [ ] Analytics midiendo impacto de cada pieza
- [ ] Todo documentado en spec 019

---

**Spec**: spec.md
**Plan**: plan.md
**Tasks**: tasks.md
**Checklist**: checklist.md
**Research**: research.md
**Data Model**: data-model.md
**Contracts**: contracts/README.md
