# Session 2026-07-13: SDC Agent OS — Arquitectura Completa

## ¿Qué pasó en esta sesión?

Se transformó Sonora Digital Corp de un stack desordenado (Jarvis, Hermes, Sonora Engine por separado) a una **arquitectura de 3 capas limpia**: OpenCode como cerebro, SDC Core como plataforma, Smart Apps como productos.

---

## Las 3 Capas

### 1. OPENCODE (Cerebro)
**No se duplica — se usa lo nativo:**

| Componente | Qué hace | Cómo se usa |
|-----------|----------|-------------|
| `explore` | Buscar código nativo | `/explore` |
| `builder` | Implementar tareas | `/build` |
| `mystic` (primary) | Asistente personal | Default |
| `skills/` | Conocimiento especializado | lovable, creator, content, design |
| `commands/` | Acciones rápidas | `/design`, `/generar`, `/crear-empresa` |
| `MCP sonora-mcp` | Acceso a 49 tools | Via `sonora-mcp` MCP server |

### 2. SDC CORE (Infraestructura)
**49 MCP tools en 15 servers:**

| Server | Tools | Función |
|--------|-------|---------|
| `hasura_mcp` | 3 | GraphQL (artists, revenue, transactions) |
| `supabase_mcp` | 10 | Auth + Storage |
| `engram_mcp` | 4 | Memoria por tenant |
| `omnivoice_mcp` | 3 | Voz clonada |
| `upload_mcp` | 4 | Archivos a Supabase |
| `rag_mcp` | 3 | Búsqueda semántica en Qdrant |
| `payments_mcp` | 4 | Stripe (pendiente API key) |
| `llm_mcp` | 2 | Chat |
| `whisper_mcp` | 2 | Transcripción audio |
| `ffmpeg_mcp` | 2 | Edición de video |
| `content_mcp` | 1 | FLUX → Stable Video |
| `lora_mcp` | 2 | Entrenamiento LoRA |
| `firecrawl_mcp` | 2 | Scraping web |
| `openlovable_mcp` | 4 | Generar apps |
| `playwright_mcp` | 3 | Browser automation |

### 3. SMART APPS (Productos)
**Cada empresa es un tenant en `tenants/`:**

```
tenants/
├── abe-music/     → abe.sonoracorp.com (Next.js, 11 páginas)
│   ├── web/       → Frontend con VoiceWidget, 3D, shadcn
│   ├── api/       → Backend FastAPI (:5180)
│   ├── studio/    → Generación de video
│   └── agents/    → 6 agentes definidos
└── sdc/           → sonoradigitalcorp.com
```

---

## Lo que se limpió

| Antes | Después |
|-------|---------|
| 3 stacks paralelos (Jarvis, Hermes, Engine) | 1 stack unificado (SDC Core) |
| 2 MCP gateways (:8000 + :8180) | 1 MCP gateway (:8180) |
| 2 ABE frontends (abe/ + abe-next/) | 1 frontend (sonora-web) |
| 5 docker-compose files | 2 files (core + products) |
| 3 servicios zombie corriendo | 0 zombies |
| 25 MCP tools | 49 MCP tools |
| 0 agentes definidos | 9 agentes definidos |
| 0 herramientas documentadas | 49 herramientas documentadas |

---

## Skills (conocimiento, no agentes)

| Skill | Archivo | Una función |
|-------|---------|-------------|
| **lovable** | `skills/lovable/SKILL.md` | Generar apps React |
| **creator** | `skills/creator/SKILL.md` | Crear empresas |
| **content** | `skills/content/SKILL.md` | Pipeline de contenido |
| **design** | `skills/design/SKILL.md` | UI con shadcn/three.js |

---

## Pipeline de contenido

```
6:00 AM — CRON
  1. Hasura → stats del día
  2. RAG → contexto (noticias + tendencias)
  3. LLM → genera script
  4. FAL FLUX + LoRA → imagen del artista
  5. Stable Video → anima imagen a video (5s)
  6. FFmpeg → 4 formatos (TikTok, Reels, Shorts, FB)
  7. Supabase Storage → guarda
  8. Engram → registra
  9. Telegram → notifica
```

---

## Pendiente

| Tarea | Bloqueante |
|-------|-----------|
| Stripe API key | Pagos reales |
| GRAFANA startup | Esperar ~2min |
| PROMPTFOO model ID | Fix modelo en OpenRouter |

---

## Comandos rápidos

```
/design "hero con 3D para ABE Music"     → UI component
/generar-campaña "verano" --artista Hector → contenido
/crear-empresa "Nueva Empresa"            → deploy empresa
/status                                     → healthcheck
```
