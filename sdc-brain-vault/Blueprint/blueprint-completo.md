# BLUEPRINT — Sonora Digital Corp
## Arquitectura Global del Ecosistema

| Versión | Fecha | Autor |
|---------|-------|-------|
| 1.0.0 | 2026-07-18 | Mystic (SDC Orchestrator) |

---

## Índice

1. [Visión General](#1-visión-general)
2. [Infraestructura Física](#2-infraestructura-física)
3. [Stack Tecnológico](#3-stack-tecnológico)
4. [Servicios Core](#4-servicios-core)
5. [Clone Service (Producto)](#5-clone-service-producto)
6. [Cerebro Digital](#6-cerebro-digital)
7. [Ecosistema MCP](#7-ecosistema-mcp)
8. [Arquitectura de Agentes](#8-arquitectura-de-agentes)
9. [Memoria y Persistencia](#9-memoria-y-persistencia)
10. [Pipeline SDD](#10-pipeline-sdd)
11. [Seguridad y Secrets](#11-seguridad-y-secrets)
12. [Monitoreo y Observabilidad](#12-monitoreo-y-observabilidad)
13. [Flujo de Desarrollo](#13-flujo-de-desarrollo)
14. [Roadmap y Próximos Pasos](#14-roadmap-y-próximos-pasos)

---

## 1. Visión General

### 1.1 Propósito

Sonora Digital Corp es una plataforma integral de agentes AI para la industria musical y publicitaria. El sistema combina:

- **Automatización de marketing musical**: colectores de datos multi-plataforma, análisis de artistas, generación de contenido
- **Clonación publicitaria**: Servicio de clon facial y vocal para campañas de marketing (producto nuevo)
- **Cerebro digital personal**: Extensión de la mente del fundador (Luis Daniel Guerrero Enciso) con memoria persistente

### 1.2 Principios Arquitectónicos

```
1. Stack Lock — No cambiar tecnologías core sin ADR
2. GPU-as-a-Service — Sin GPU local; todo el procesamiento visual via FAL.ai
3. Memoria 3-capas — Working (sesión), Project (semanas), Knowledge (permanente)
4. Agent-First — Todo es accesible via agentes conversacionales (OpenClaw)
5. SDD Governance — Toda feature sigue SPEC → Gherkin → TDD → MCP → Docs
```

### 1.3 Dominios de Negocio

| Dominio | Descripción | Estado |
|---------|-------------|--------|
| Music Intelligence | Colectores, análisis, scoring de artistas | ✅ Activo |
| ABE Music OS | PWA para Abraham Ortega (CEO ABE Music) | ✅ Activo |
| Clone Service | Clonación facial/vocal para publicidad | 🆕 Lanzado |
| Digital Brain | Memoria personal de Luis Daniel | 🆕 Lanzado |
| Call Engine | Llamadas WhatsApp salientes con AI | 🧪 Experimental |

---

## 2. Infraestructura Física

### 2.1 Máquinas

#### sdc-prod (VPS OVH)

| Atributo | Valor |
|----------|-------|
| **IP** | `149.56.46.173` |
| **IPv6** | `2607:5300:229:74d::1` |
| **Hostname** | `sdc-prod.vps.ovh.ca` |
| **OS** | Ubuntu 26.04 LTS |
| **RAM** | 11 GB |
| **Disco** | 96GB (64% usado) |
| **Swap** | 2GB (100% usado) |
| **Rol** | Servidor principal de producción |
| **Acceso** | `ssh ovh` (configurado en `~/.ssh/config`) |

#### mysticpc (Laptop Local)

| Atributo | Valor |
|----------|-------|
| **Propietario** | Luis Daniel Guerrero Enciso |
| **OS** | Linux (Ubuntu) |
| **IP** | Dinámica (México, 187.245.106.218) |
| **Rol** | Estación de desarrollo |
| **Display** | Sí (Firefox, Obsidian) |
| **Acceso desde VPS** | ❌ No accesible (NAT) |

### 2.2 Puertos y Servicios — Mapa Completo

```
22/tcp    SSH                     → Público
80/tcp    HTTP nginx              → Público → sonoradigitalcorp.com
443/tcp   HTTPS nginx             → Público → sonoradigitalcorp.com

5432/tcp  PostgreSQL 15           → 127.0.0.1 (Docker)
6379/tcp  Redis 7                 → 127.0.0.1 (Docker)
7687/tcp  Neo4j Bolt              → 127.0.0.1 (Docker)
7474/tcp  Neo4j HTTP              → 127.0.0.1 (Docker)
6333/tcp  Qdrant HTTP             → 127.0.0.1 (Docker)
6334/tcp  Qdrant gRPC             → 127.0.0.1 (Docker)

3000/tcp  LangFuse                → 127.0.0.1 (Docker)
5678/tcp  n8n                     → 127.0.0.1 (Docker)
8000/tcp  Hermes MCP Gateway      → 127.0.0.1 (Docker)

8765/tcp  Content Server MCP      → 127.0.0.1 (Docker)
8766/tcp  Edge TTS API            → 127.0.0.1 (Docker)
3900/tcp  OmniVoice               → 127.0.0.1 (Docker)
8502/tcp  Open Notebook UI        → 127.0.0.1 (Docker)
5055/tcp  Open Notebook API       → 127.0.0.1 (Docker)

18789/tcp OpenClaw Gateway        → 127.0.0.1 (systemd)
9090/tcp  WhatsApp WACLI          → 127.0.0.1 (Docker)
3003/tcp  Telegram Bot            → 127.0.0.1 (Docker)
11434/tcp Ollama                  → 127.0.0.1 (systemd)
```

### 2.3 Docker Volumes

```
pg_data            → PostgreSQL principal
redis_data         → Caché y colas
neo4j_data         → Grafo de conocimiento
qdrant_storage     → Vectores semánticos
n8n_data           → 33 workflows de automatización
langfuse_data      → Trazas de LLM
openclaw_*         → Gateway, extensiones, memoria
engram_data        → Memoria persistente (SQLite WAL)
voice_models       → Modelos de voz clonados
wacli_*            → WhatsApp bridge
omnivoice_data     → Voice cloning Studio
```

---

## 3. Stack Tecnológico

### 3.1 Lenguajes y Runtimes

| Tecnología | Versión | Uso |
|-----------|---------|-----|
| Python | 3.10+ | Backend APIs, MCP servers, scripts, ML |
| Node.js | 22.23.1 | OpenClaw, MCP gateway, npm ecosystem |
| Go | 1.22+ | Call Engine (llamadas WhatsApp) |
| TypeScript | 5.x | Playwright tests, MCP tools |
| Bash | - | DevOps scripts, deploy, sync |

### 3.2 Frameworks y Librerías Core

| Librería | Uso |
|----------|-----|
| FastAPI | APIs REST (ABE Service, Hermes, Jarvis) |
| httpx | Async HTTP para MCP tools → FAL.ai, OmniVoice, Supabase |
| SQLite3 | Persistencia local (Clone Service credits, Engram) |
| pytest | Framework de tests (95 tests) |
| ruff | Linter (0 errores) |
| Playwright | E2E testing |
| FFmpeg | Procesamiento de video/audio |

### 3.3 Bases de Datos

| DB | Tipo | Puerto | Propósito |
|---|------|--------|-----------|
| PostgreSQL 15 | Relacional | 5432 | Datos core del sistema |
| Neo4j 5.19 | Grafo | 7687 | Relaciones entre entidades |
| Qdrant 1.7.4 | Vectorial | 6333 | Búsqueda semántica |
| Redis 7 | KV/Cache | 6379 | Caché, colas, rate limiting |
| SQLite (Engram) | Documento | 7437 | Memoria persistente (WAL mode) |
| SQLite (Clone) | Relacional | - | Créditos y clientes (archivo) |

### 3.4 Proveedores AI

| Proveedor | Modelos | API Key |
|-----------|---------|---------|
| OpenCode | deepseek-v4-flash-free | `sk-8dX1i0...` |
| OpenRouter | gpt-4o, claude-3.5, gemini-2.5, llama-3.3 | `sk-or-v1-4674...` |
| Ollama (local) | qwen2.5:1.5b, llama3.2:3b, deepseek-r1:7b | - |
| FAL.ai | flux-lora, flux-dev, kling, seedance | `FAL_API_KEY` configurado |
| ElevenLabs | TTS (fallback) | Configurado en content server |
| Supabase | Auth, Storage, DB | `DB_URL` + service key |

---

## 4. Servicios Core

### 4.1 OpenClaw Gateway

```
Estado: ✅ Activo (systemd)
Puerto: 18789
Versión: 2026.7.1
Plugins: 10 (browser, canvas, device-pair, file-transfer, memory-core, ollama, phone-control, talk-voice, telegram, whatsapp)
Skills: 4 (browser-automation, canvas, clone-service, wacli)
```

El gateway es el punto de entrada conversacional. Los skills se cargan desde `~/.openclaw/plugin-skills/` y se inyectan en el prompt del agente.

**Skills instalados:**
- `browser-automation` — Automatización de navegador
- `canvas` — Generación de imágenes canvas
- **`clone-service`** 🆕 — Flujo completo de clon publicitario (SKILL.md, 3.2KB)
- `wacli` — Mensajería WhatsApp via wacli CLI

### 4.2 MCP Ecosystem

```
Gateway:          sonora-mcp-gateway (puerto 18989, ~108 tools)
Servers Python:   16 (content, engram, ffmpeg, firecrawl, hasura, llm, lora, 
                  mercadopago, omnivoice, openlovable, payments, playwright,
                  rag, supabase, upload, whisper)
JS Tools:         34 tool definitions
```

**MCP Tools del Clone Service 🆕:**

| Tool | Server | Inputs |
|------|--------|--------|
| `validate_photos` | `lora_mcp.py` | photo_urls[], client_id |
| `train_lora` | `lora_mcp.py` | client_id, photo_urls[], trigger_word |
| `check_face_quality` | `lora_mcp.py` | photo_url |
| `validate_audio` | `voice_clone_mcp.py` | audio_url, client_id |
| `clone_voice` | `voice_clone_mcp.py` | audio_url, client_id, name |
| `list_voices` | `voice_clone_mcp.py` | client_id |
| `generate_tts` | `voice_clone_mcp.py` | text, voice_id |
| `gen_photo` | `generate_mcp.py` | client_id, prompt, lora_id |
| `gen_video` | `generate_mcp.py` | client_id, prompt, style |
| `gen_tts` | `generate_mcp.py` | client_id, text, voice_id |
| `create_pack` | `credit_mcp.py` | client_id, pack_type |
| `consume_credit` | `credit_mcp.py` | client_id, asset_type |
| `get_credits` | `credit_mcp.py` | client_id |
| `ffmpeg_convert` | `ffmpeg_mcp.py` | video_url, target |
| `ffmpeg_assemble` | `ffmpeg_mcp.py` | video_url, audio_url, watermark |
| `ffmpeg_multiformat` | `ffmpeg_mcp.py` | video_url, platform[] |

### 4.3 n8n Workflows

```
33 workflows activos que incluyen:
├── agenda_diaria
├── alarm_530_quantum
├── content_pipeline
├── whatsapp_personal_mystic
├── watchdog_self_healing
├── social_media_auto
├── health_check_sistema
└── hermes-briefing_matutino
```

---

## 5. Clone Service (Producto)

### 5.1 Descripción General

Servicio de clon publicitario donde el cliente paga un pack, envía fotos y audio por WhatsApp/Telegram, y recibe contenido con su identidad visual y vocal para campañas de marketing.

```
SPEC:     SPEC-20260718-CLONE-SERVICE (Tier 3, Score 82/100)
FRs:      6 (Recolección → Validación → Entrenamiento → Generación → Entrega → Créditos)
Gherkin:  5 features, 19 escenarios
Tests:    95 (unit + integration + playwright)
MCP:      5 servers, 16 tools
Estado:   🆕 Lanzado
```

### 5.2 Arquitectura del Pipeline

```
CLIENTE (WhatsApp/Telegram)
       │
       ▼
┌─────────────────────────────────────────────────┐
│            OPENCLAW GATEWAY (:18789)             │
│  Skill: clone-service (SKILL.md — 3.2KB)        │
│  Flujo: recibir fotos → contar → validar →      │
│         detectar "terminé" → entrenar → generar  │
└──────────────────────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────┐
│              PIPELINE CLI (scripts/)             │
│                                                  │
│  clone_pipeline.py                               │
│  ├── create-pack  → SQLite: clients table        │
│  ├── validate     → SQLite: photos + audio       │
│  ├── train        → FAL.ai (LoRA) + OmniVoice    │
│  ├── generate     → FAL.ai (flux-lora, kling)    │
│  ├── status       → SQLite: summaries            │
│  └── consume      → SQLite: decrement credits    │
└──────────────────────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────┐
│              CAPA DE ALMACENAMIENTO              │
│                                                  │
│  Supabase Storage (sdc-assets)                   │
│  └── /clients/{id}/raw/photos/                   │
│  └── /clients/{id}/raw/audio/                    │
│  └── /clients/{id}/models/lora.safetensors       │
│  └── /clients/{id}/models/voice/{voice_id}/      │
│  └── /clients/{id}/output/photos/{uuid}.jpg      │
│  └── /clients/{id}/output/videos/{uuid}.mp4      │
│  └── /clients/{id}/output/audio/{uuid}.wav       │
│                                                  │
│  SQLite (data/clone_service.db)                  │
│  └── clients, photos, audio, assets tables       │
└──────────────────────────────────────────────────┘
```

### 5.3 Flujo Conversacional (OpenClaw Skill)

```
Fase 1: RECEPCIÓN
  Cliente: "Quiero el pack de clon publicitario"
  Agente:  "¡Perfecto! Necesito 15-20 fotos tuyas + audio de 30s"
  
  Cliente: envía foto 1, foto 2, ..., foto 15
  Agente:  "Recibida foto 3/15. ¡Sigue enviando!"
  
  Cliente: "Terminé"
  Agente:  valida → "Material completo. Empiezo entrenamiento (~10 min)"

Fase 2: ENTRENAMIENTO (automático)
  → FAL.ai flux-lora-trainer (15-20 fotos → LoRA weights)
  → OmniVoice / MiniMax voice clone (30s audio → voice model)
  → Notifica: "¡Listo! Ya puedes pedir contenido con tu cara y voz"

Fase 3: GENERACIÓN (bajo demanda)
  Cliente: "Foto mía en oficina ejecutiva, traje azul"
  Agente:  gen_photo(client_id, prompt) → descuenta 1 crédito
  
  Cliente: "Video de 15s presentando mi producto"
  Agente:  gen_video(client_id, script) + lip sync → descuenta 5 créditos
  
  Cliente: "Dilo en mi voz: 'Visita nuestra web'"
  Agente:  gen_tts(text, voice_id) → descuenta 1 crédito

Fase 4: ENTREGA
  → FFmpeg: convert a 9:16 (TikTok), 16:9 (YouTube), 1:1 (Instagram)
  → Supabase Storage: entrega pública
  → Enlaces expiran a los 30 días
```

### 5.4 Modelo de Pricing

| Pack | Precio | Fotos | Videos | TTS | Training |
|------|--------|-------|--------|-----|----------|
| Basic | $49 | 10 | 3 | 10 | 1 |
| Pro ⭐ | $99 | 30 | 10 | 30 | 1 |
| Enterprise | $199 | 100 | 30 | 100 | 3 |

**Costos reales (FAL.ai):**
- Entrenamiento LoRA: ~$3-5
- Clon de voz: ~$1
- Foto generada: ~$0.01
- Video 15s: ~$0.15
- **Margen: >90%**

### 5.5 Stack Técnico del Clone Service

| Capacidad | Solución | Por qué |
|-----------|----------|---------|
| LoRA Training | FAL.ai flux-lora-trainer | Sin GPU local |
| Image Gen | FAL.ai flux-lora + LoRA | Serverless, $0.01/foto |
| Video Gen | FAL.ai kling/seedance + veed-lipsync | Calidad profesional |
| Voice Clone | OmniVoice (:3900) + MiniMax | Local + cloud backup |
| Storage | Supabase Storage (sdc-assets) | Ya configurado |
| Cache/Process | Content Server (:8765) + FFmpeg | Post-procesamiento |
| Payments | Stripe / Mercado Pago | Integración existente |

---

## 6. Cerebro Digital

### 6.1 Concepto

El Cerebro Digital es una extensión de Luis Daniel Guerrero Enciso — memoria persistente con capas de corto, mediano y largo plazo, accesible visualmente via Obsidian.

```
CAPAS DE MEMORIA:
├── Layer 1: Working (corto plazo)
│   ├── Sesión activa de opencode
│   ├── Contexto actual del agente
│   └── Se pierde al cerrar sesión
│
├── Layer 2: Project (mediano plazo)
│   ├── Proyectos activos (SDD specs, sprints)
│   ├── Decisiones arquitectónicas recientes
│   └── Persiste semanas/meses
│
├── Layer 3: Knowledge (largo plazo)
│   ├── Engram DB (SQLite WAL, 347+ observaciones)
│   ├── Qdrant (vectores para búsqueda semántica)
│   ├── Neo4j (grafo de relaciones)
│   └── Persiste permanentemente
│
└── Layer 4: Identity (permanente)
    ├── OMEGA PROMPT v10.0
    ├── SOUL.md + TRUTH.md + Constitution
    ├── AGENTS.md + reglas del sistema
    └── Nunca se modifica sin ADR
```

### 6.2 Vault de Obsidian

```
📁 ~/Documents/sdc-brain-vault/
├── 📁 .obsidian/
│   ├── app.json              ← Configuración del vault
│   ├── core-plugins.json     ← Plugins esenciales (10)
│   └── community-plugins.json ← Solo Dataview (ligero)
│
├── 📁 Dashboard/
│   └── Digital Brain.md      ← Panel principal con navegación
│
├── 📁 People/                ← Contactos
│   ├── Luis Daniel Guerrero Enciso.md   ← YO
│   ├── Perroni.md                      ← CEO SDC
│   ├── Nathaly Hermosillo.md           ← Contacto personal
│   ├── Abraham Ortega.md               ← CEO ABE Music
│   └── Noel Nichols.md                 ← Socio creativo
│
├── 📁 Projects/              ← Proyectos activos
│   ├── Sonora Digital Corp.md          ← Core platform
│   └── Clone Service.md                ← Producto nuevo
│
├── 📁 Decisions/             ← Decisiones arquitectónicas
│   ├── Backend IA FAL.ai.md
│   └── Almacenamiento Supabase.md
│
├── 📁 Learnings/             ← Descubrimientos y aprendizajes
├── 📁 Graph/                 ← Relaciones
│   └── relationships.md      ← Mermaid graph + Dataview
│
├── 📁 Observations/          ← Export automático de Engram
├── 📁 Sessions/              ← Historial de sesiones
├── 📁 Templates/             ← Plantillas
│   ├── person.md             ← Nueva persona
│   ├── decision.md           ← Nueva decisión
│   ├── learning.md           ← Nuevo aprendizaje
│   └── project.md            ← Nuevo proyecto
│
└── 📁 Canvas/                ← Mapas visuales
```

### 6.3 Ciclo de Sincronización

```
Engram DB ──→ sync-brain-vault.sh ──→ Obsidian Vault
(SQLite WAL)      │                    (Markdown files)
                  ├── Export observaciones
                  ├── Generar People
                  ├── Generar Projects
                  └── Generar Decisions
                  │
                  └──→ Google Drive Backup
                       (GVFS mount)
```

### 6.4 Comandos del Cerebro

```bash
brain-sync      # Sincroniza Engram → Obsidian + Google Drive
brain-open      # Abre Obsidian con el vault (AppImage, --no-sandbox)
brain-status    # Muestra estado: observaciones, personas, decisiones
```

---

## 7. Ecosistema MCP

### 7.1 Arquitectura MCP

```
                    ┌──────────────────────┐
                    │   OpenCode / Agent    │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │  MCP Gateway (:18989) │
                    │  108 tools total      │
                    └──────────┬───────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
   ┌────────────┐     ┌──────────────┐     ┌──────────────┐
   │ Python MCPs │     │  JSON MCPs   │     │  JS Tools    │
   │ 16 servers  │     │  6 configs   │     │  34 tools    │
   └────────────┘     └──────────────┘     └──────────────┘
```

### 7.2 Servidores Python (16)

| Server | Puerto | Tools | Propósito |
|--------|--------|-------|-----------|
| `content_mcp` | - | manage content | Gestión de contenido |
| `engram_mcp` | 7437 | mem_* (14 tools) | Memoria persistente |
| `ffmpeg_mcp` | - | convert, assemble, multiformat | Video/audio processing |
| `whisper_mcp` | - | transcribe | Speech-to-text |
| `supabase_mcp` | - | signup, login, storage | Supabase operations |
| `lora_mcp` | - | validate_photos, train_lora, check_face | LoRA training |
| `voice_clone_mcp` | - | validate_audio, clone, tts | Voice cloning |
| `generate_mcp` | - | gen_photo, gen_video, gen_tts | Content generation |
| `credit_mcp` | - | create_pack, consume, get | Credit system |
| `rag_mcp` | - | query, search | RAG queries |
| `llm_mcp` | - | chat, complete | LLM calls |
| `payments_mcp` | - | create, process | Mercado Pago / Stripe |
| `playwright_mcp` | - | browse, screenshot | Browser automation |
| `omnivoice_mcp` | - | speak, clone, list | OmniVoice interface |
| `mercadopago_mcp` | - | payment, webhook | Mercado Pago API |
| `upload_mcp` | - | upload | File upload |

---

## 8. Arquitectura de Agentes

### 8.1 OpenCode Agents (20+)

| Agent | Modo | Rol |
|-------|------|-----|
| `mystic` | primary | Orquestador principal del sistema |
| `hermes` | subagent | Gateway multi-canal |
| `openclaw` | subagent | 55 skills especializadas |
| `sdd` | subagent | SDD pipeline orchestrator |
| `sdd-*` (5) | subagent | Spec, Design, Apply, Verify, Archive |
| `sales/dev/support/*` (10) | subagent | Operating Systems por dominio |
| `builder/reviewer/...` | subagent | Roles específicos |

### 8.2 Agent Registry (`agents/registry.yaml`)

| Agent | Tenant | Tools | Channel |
|-------|--------|-------|---------|
| **creator-agent** | sdc | lovable, hasura, upload, engram | agent:creator |
| **quality-agent** | sdc | llm, engram_search, rag | agent:quality |
| **monitor-agent** | sdc | engram_save, telegram_notify | agent:monitor |
| **ceo-agent** | abe-music | hasura, engram, rag, llm | agent:ceo |
| **marketing-agent** | abe-music | rag, llm, engram, firecrawl | agent:marketing |
| **content-agent** | abe-music | rag, llm, video, tts, whisper | agent:content |
| **sales-agent** | abe-music | stripe, supabase, engram | agent:sales |
| **support-agent** | abe-music | rag, engram, llm, omnivoice | agent:support |
| **voice-agent** | abe-music | omnivoice, whisper, llm, rag | agent:voice |
| **clone-agent** 🆕 | **sdc** | **validate,train,clone,gen,credit,ffmpeg** | **agent:clone** |

### 8.3 Agent Harness — Clone Agent 🆕

```
Mission: Gestionar el ciclo de vida del clon publicitario
Capabilities: clone-person → 8 eventos
Skills: clone-recollection, clone-training, clone-generation, clone-delivery
Memory: Layer 1 (working) + Layer 3 (project)
Approval: Training = auto, Generation = auto, Refund = approve
Failure Modes: 6 (FAL timeout, bad photos, low similarity, upload fail, etc.)
Recovery: Retry backoff, notify client, fallback formats
```

---

## 9. Memoria y Persistencia

### 9.1 Engram (Memoria Principal)

```
DB:       ~/.engram/engram.db (SQLite WAL)
Tamaño:   ~3.7MB + 4.2MB WAL
Obs:      347+
Sesiones: 319
Prompts:  126
Puerto:   7437 (HTTP server)
```

**Tipos de observaciones:**
| Tipo | Descripción | Ejemplo |
|------|-------------|---------|
| `command` | Comandos bash ejecutados | `git commit -m "feat: ..."` |
| `config` | Variables de entorno, git status | `SDC_PROJECT=test` |
| `architecture` | Decisiones de infraestructura | `Backend IA: FAL.ai` |
| `decision` | Decisiones de diseño | `Almacenamiento: Supabase` |
| `bugfix` | Errores corregidos | `FTS5 query sanitization` |
| `learning` | Aprendizajes y descubrimientos | `GVFS file IDs` |
| `discovery` | Hallazgos generales | `perrykingla.69@gmail.com` |
| `milestone` | Hitos completados | `Clone Service Implementation` |

### 9.2 Bases de Datos — Mapa Completo

| DB | Tipo | Datos | Tamaño estimado |
|----|------|-------|----------------|
| PostgreSQL 15 | Relacional | Usuarios, artistas, transacciones | ~2GB |
| Neo4j 5.19 | Grafo | Relaciones entre entidades | ~500MB |
| Qdrant 1.7.4 | Vectorial | Embeddings semánticos | ~300MB |
| Redis 7 | KV/Cache | Sesiones, colas, rate limits | ~100MB |
| Engram SQLite | Documento | Memoria persistente (WAL) | ~8MB |
| Clone SQLite 🆕 | Relacional | Clientes, créditos, assets | ~1MB |

### 9.3 Políticas de Retención

| Tipo | Retención | Acción |
|------|-----------|--------|
| Assets generados (Clone) | 30 días | Expira automática en Supabase |
| Engram observations | Permanente | Backup via `engram sync` |
| Logs de sesión | 90 días | Rotación automática |
| Fotos raw de clientes | 7 días post-entrenamiento | Política configurable |
| Modelos LoRA | Permanente | Almacenados en Content Server |

---

## 10. Pipeline SDD

### 10.1 Metodología

Todo cambio en el sistema sigue el pipeline SDD (HAS-007):

```
1. MISSION      → Propósito, north star, objetivo de negocio
2. CONSTITUTION → Validar contra constitution YAMLs
3. RESEARCH     → Papers, benchmarks, competidores, experimentos
4. ARCHITECTURE → ADR, patrones, contratos, capability mapping
5. SIMULATION   → Riesgo, costo, seguridad
6. SPECIFICATION → SDD con Gherkin + FRs + Score
7. IMPLEMENTATION → Código + tests (BDD + TDD)
8. VERIFICATION   → Gates: constitution + tests + lint + score
9. OBSERVABILITY  → Deploy + monitor + trace + alert
10. EVOLUTION     → Score → ADR → Refactor → Update prompts → Close session
```

### 10.2 Tier System

| Tier | Scope | Pipeline Stages | Score Requerido |
|------|-------|----------------|-----------------|
| 0 | Typo, config, comment | 7→8 | - |
| 1 | Quick fix, minor bug | 3→7→8→9 | - |
| 2 | Feature, improvement | 4→6→7→8→9 | ≥60 |
| 3 | Capability, platform | 1→2→3→4→5→6→7→8→9→10 | ≥75 |

### 10.3 Gates de Verificación

```
Gate 0: Sync Gate       → git status limpio
Gate 1: Constitution    → 6 sub-gates (Policy, Security, Cost, Compliance, Quality, Knowledge)
Gate 2: Tests Gate      → pytest tests/ -q (95 tests)
Gate 3: Lint Gate       → ruff check (0 errores)
Gate 4: Score Gate      → score ≥75 (Tier 3)
Gate 5: ADR Gate        → ADR-*.md existe (Tier 3)
```

### 10.4 Artifacts de Sesión

Cada sesión SDD genera:

```
process/completed/{SPEC_ID}/
├── SPEC.md          ← Especificación
├── SCORE.md         ← Evaluación de score
├── ADR.md           ← Decisiones arquitectónicas
├── LECCION.md       ← Lecciones aprendidas
├── events.jsonl     ← Traza de eventos
├── gherkin/         ← Características BDD
├── plan.md          ← Plan de implementación
└── tasks.md         ← Desglose de tareas
```

---

## 11. Seguridad y Secrets

### 11.1 Gestión de Secrets

```
Método: age encryption (X25519)
Archivos encriptados:
├── .env.age                  ← Variables de entorno
├── config/.secrets/clients.json.age  ← Secrets de clientes
└── auth.json.age             ← Auth tokens

Variables de entorno críticas:
├── FAL_API_KEY                   ← API key de FAL.ai (GPU serverless)
├── OPENROUTER_API_KEY        ← API key de OpenRouter
├── DB_URL + API_KEY ← Supabase
├── POSTGRES_PASSWORD         ← DB principal
├── NEO4J_PASSWORD            ← Graph DB
├── REDIS_PASSWORD            ← Cache
└── LANGFUSE_*                ← Observabilidad LLM
```

### 11.2 Políticas de Seguridad

```
1. NO hardcodear secrets en código (todos via .env o age)
2. NO bindear servicios a 0.0.0.0 (solo 127.0.0.1 + nginx)
3. UFW: solo puertos 22, 80, 443, 8080, 5180, 8085
4. Docker userland-proxy: false (raw table iptables)
5. Secrets filtrados en auto-capture (API_KEY, TOKEN, PASSWORD)
```

---

## 12. Monitoreo y Observabilidad

### 12.1 Stack de Observabilidad

| Herramienta | Propósito | Puerto |
|-------------|-----------|--------|
| LangFuse | Trazas de LLM, costos, latencia | 3000 |
| n8n | Automatización y monitoreo | 5678 |
| Truth Guardian | Scoreboard y health checks | 8088 |
| Evolution Dashboard | Presentaciones de estado | 8080 |

### 12.2 Eventos del Sistema

**Clone Service Events (8 eventos):**

| Evento | Trigger |
|--------|---------|
| `clone.client_registered` | Pack comprado |
| `clone.photos_collected` | 15+ fotos recibidas |
| `clone.photos_rejected` | Foto inválida |
| `clone.training_started` | Entrenamiento LoRA inicia |
| `clone.lora_trained` | LoRA completado |
| `clone.voice_cloned` | Voz clonada |
| `clone.generated` | Asset generado |
| `clone.credits_low` | Créditos < 20% |

### 12.3 Métricas de Salud

```
Clone Service:
├── Training time: < 15 min
├── Face similarity: > 0.75
├── Generation cost: < $0.20/asset
├── Delivery formats: ≥ 3
├── Tests: 95 pasando
└── Lint: 0 errores
```

---

## 13. Flujo de Desarrollo

### 13.1 Workflow Diario

```bash
# 1. Iniciar sesión
cd /home/mystic/sonora-digital-corp
opencode

# 2. Desarrollo
/sdd-new          # Nueva feature (SDD pipeline)
/plan             # Descomponer objetivo en tareas
/build            # Construir feature
/test             # pytest tests/ -q
/verify           # Constitution Gate

# 3. Commits y push
git add -A && git commit -m "feat: ..."
git push

# 4. Sincronizar cerebro
brain-sync        # Engram → Obsidian + Google Drive

# 5. Cerrar sesión
/doc              # Auto-generar docs de proceso
/close            # Close session script
```

### 13.2 Comandos Rápidos

```bash
# Clone Service
clone-test        # 95 tests
clone-flow        # Test pipeline completo (8 pasos)
clone-quantum     # Presentación cuántica en Firefox
clone-help        # Ayuda de comandos
clone-spec        # Leer SPEC
clone-ls          # Listar archivos del clone
clone-status X    # Estado del cliente X

# Cerebro Digital
brain-sync        # Sincronizar Engram → Obsidian
brain-open        # Abrir Obsidian vault
brain-status      # Estado del cerebro

# Sistema
sdc-status        # Verificar repo correcto
mystic-status     # System overview
```

### 13.3 SDD Commands

```bash
/sdd-new          # Nueva especificación
/sdd-spec         # Generar SPEC
/sdd-design       # Crear plan.md + tasks.md
/sdd-apply        # Implementar
/sdd-verify       # Validar gates
/sdd-archive      # Documentar y cerrar
```

---

## 14. Roadmap y Próximos Pasos

### 14.1 Estado Actual (Julio 2026)

| Área | Estado | Score |
|------|--------|-------|
| Clone Service | 🆕 Lanzado | 82/100 |
| Cerebro Digital | 🆕 Lanzado | - |
| ABE Music OS | ✅ Estable | - |
| Music Intelligence | ✅ Estable | - |
| Call Engine | 🧪 Experimental | - |
| OpenClaw Integration | 🔄 En progreso | - |

### 14.2 Próximos Pasos Inmediatos

```
1. Probar pipeline real contra FAL.ai sandbox
   → test_clone_flow.sh con client_id real
   → Verificar costos reales de FAL

2. Deploy a VPS
   → bash scripts/sync-to-vps.sh
   → Verificar clone-service skill en VPS

3. Probar flujo completo con OpenClaw agent
   → Enviar mensaje por WhatsApp/Telegram
   → Verificar que el skill responde correctamente

4. Dashboard visual para clientes
   → Web app donde el cliente ve sus assets
   → Historial de generaciones y créditos restantes
```

### 14.3 Visión a Largo Plazo

```
Q3 2026:
├── Clone Service: 50+ clientes activos
├── Dashboard de autoservicio para clientes
├── GPU propia (RunPod) si volumen >50 clientes/mes

Q4 2026:
├── FaceFusion como backend adicional
├── Sistema de colas y workers dedicados
├── API pública para integración con agencias

2027:
├── 1000+ clientes/mes
├── Migración a PostgreSQL para créditos
├── Expansión a video real-time (LivePortrait streaming)
```

---

*Blueprint generado por Mystic (SDC Orchestrator) — 2026-07-18*
*95 tests · 0 lint · Score 82/100 · 28 archivos · 5 MCP servers 🆕*
