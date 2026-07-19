# 🌌 Sonora OS — Blueprint Cuántico

```
                   ╱▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔╲
                  ╱   SONORA OS v3    ╲
                 ╱    Sistema Auto-    ╲
                ╱     consciente        ╲
               ╱     ───────────        ╲
              ╱    "El sistema que      ╱
             ╱     se conoce solo"     ╱
            ╱_________________________╱
```

**Versión:** 3.0.0 · **Branch:** main (`ff4f25b`) · **Fecha:** 2026-07-19  
**Fundación:** 31 apps core · 54 skills · 26 MCP servers · 74 agentes · 14 productos · 118 eventos  
**VPS:** 29 containers Docker · 6 systemd services · 4/6 health online  

---

## 🌱 Dónde VENÍAS — El Estado de Superposición Inicial

El sistema empezó como una **función de onda cuántica** sin colapsar:

```
|ψ_inicial⟩ = 0.2|skills⟩ + 0.2|productos⟩ + 0.2|ADRs⟩ + 0.4|caos⟩
```

Cada parte existía en **superposición**: un skill era y no era completo a la vez. Los MCP servers peleaban por ser el mismo (2 servers de WhatsApp). OpenClaw prometía 42 skills pero solo 1 existía en el repo. Hermes tenía 12 skills en JSON que nadie más podía usar. 10 skills tenían el cartel de "en construcción".

**Analogía cuántica:** Como el gato de Schrödinger — el sistema estaba vivo y muerto simultáneamente. Cada vez que abrías una skill, no sabías si estaba completa o era un esqueleto.

---

## 📍 Dónde ESTÁS — El Colapso de la Función de Onda

Hoy el sistema **colapsó a un estado definido** mediante múltiples observaciones (sesiones de trabajo):

```
|ψ_actual⟩ = 1.0|sistema_coherente⟩
```

Cada componente ahora **sabe qué es, dónde está y cómo hablar con los demás**. Es un sistema **entrelazado**: cuando un evento ocurre en WhatsApp, el Notifier lo sabe, el Tracker lo registra, el Catalog lo indexa, y el Command Center lo muestra.

---

## 📐 El Árbol del Sistema

```
sonora-digital-corp/
│
├── ⚛️ CORE — 31 apps (el núcleo cuántico)
│   ├── apps/observe/          Nivel 1: Observar  — Eventos, collectors
│   ├── apps/understand/       Nivel 2: Entender  — Conocimiento, memoria
│   ├── apps/decide/           Nivel 3: Decidir   — Planificación, economics
│   ├── apps/act/              Nivel 4: Actuar    — Agentes, capabilities
│   ├── apps/measure/          Nivel 5: Medir     — Scoreboard, guardian
│   ├── apps/learn/            Nivel 6: Aprender  — Evolución, heurísticas
│   ├── apps/control/          Nivel 7: Control   — Dashboard unificado
│   │
│   ├── apps/sonora_engine/    Motor principal (FastAPI + WebSocket)
│   ├── apps/voice/            Pipeline de voz (STT + TTS + clonación)
│   ├── apps/whatsapp/         Webhook WhatsApp (NUEVO)
│   ├── apps/abe-service/      ABE Music OS (PWA)
│   ├── apps/brain/            Knowledge Graph + RAG
│   ├── apps/guardian/         Truth Guardian API
│   ├── apps/webui/            Web UI legacy
│   ├── apps/pack_gateway/     Pack Gateway (chat vertical)
│   ├── apps/agent_metrics/    Métricas de agentes
│   ├── apps/economics/        Cost tracking
│   ├── apps/dashboard/        Node.js dashboard
│   ├── apps/cache/            Cache layer
│   ├── apps/mcp/              MCP gateway
│   ├── apps/data/             Data processing
│   ├── apps/landing/          Landing page
│   ├── apps/learning/         Learning
│   ├── apps/logs/             Centralized logs
│   ├── apps/collectors/       Artist Intelligence collectors
│   ├── apps/agents/           Hermes client wrapper
│   ├── apps/abe/              ABE bridge
│   └── apps/SIGNAL/           React app
│
├── 🧠 SKILLS — 54 definiciones (la memoria del sistema)
│   │   Cada skill = 14 campos exactos (como un vector en el espacio de Hilbert)
│   │
│   ├── skills/root/           (44 skills)
│   │   ├── analytics          BI reports via Hasura
│   │   ├── automation         Cron jobs, workflows
│   │   ├── content            Video/reel/podcast factory
│   │   ├── creator            Agent-native companies
│   │   ├── deploy             nginx, SSL, Docker, systemd
│   │   ├── design             UI components (shadcn, three.js)
│   │   ├── monitor            Health + auto-repair
│   │   ├── nsfw               Adult content with safety filters
│   │   ├── payments           MercadoPago + Stripe
│   │   ├── social             Trend research (Playwright/Firecrawl)
│   │   ├── clone-service      Digital twin (LoRA + voice)
│   │   ├── hermes-*           (12 skills — convertidas de Telegram JSON)
│   │   ├── openclaw-*         (6 skills — plugins de OpenClaw)
│   │   ├── adr-generate       (NUEVO) Crear ADRs
│   │   ├── sdk-python         (NUEVO) Usar SDK Python
│   │   ├── adk-manage         (NUEVO) Gestionar ADK agents
│   │   ├── skill-create       (NUEVO) Meta-skill para crear skills
│   │   ├── incident-response  (NUEVO) Runbook de incidentes
│   │   ├── whatsapp-*         (2 skills) Onboarding + catálogo
│   │   └── ... + audit-security, capture-knowledge, etc.
│   │
│   └── skills/process/        (10 skills — SDD pipeline)
│       ├── sdd-spec, sdd-design, sdd-apply, sdd-verify, sdd-archive
│       ├── sdd-orchestrator, auto-doc, gsd, presentar
│       └── SKILL-TEMPLATE.md
│
├── 🔧 TOOLS / MCP — 26 servers (los brazos del sistema)
│   │   Cada MCP server = un observable cuántico
│   │
│   ├── mcp/servers/
│   │   ├── wacli_mcp.py       WhatsApp (9 tools: send, file, voice, QR, wa.me, etc.)
│   │   ├── engram_mcp.py      Memoria persistente multi-sesión
│   │   ├── ffmpeg_mcp.py      Video/audio processing
│   │   ├── generate_mcp.py    Image generation (FAL.ai + LoRA)
│   │   ├── omnivoice_mcp.py   Text-to-speech + voice cloning
│   │   ├── llm_mcp.py         Chat completion (OpenRouter, Ollama)
│   │   ├── qdrant_mcp.py      Vector search
│   │   ├── neo4j_mcp.py       Graph queries
│   │   ├── payments_mcp.py    Stripe + MercadoPago
│   │   ├── credit_mcp.py      Token credits
│   │   ├── pricing_mcp.py     Pricing engine
│   │   ├── commissions_mcp.py Commissions tracking
│   │   ├── cost_tracker_mcp.py Cost intelligence
│   │   ├── firecrawl_mcp.py   Web scraping
│   │   ├── playwright_mcp.py  Browser automation
│   │   ├── hasura_mcp.py      Hasura GraphQL
│   │   ├── upload_mcp.py      File uploads
│   │   ├── lora_mcp.py        LoRA training
│   │   ├── openlovable_mcp.py Lovable page generation
│   │   ├── onboarding_mcp.py  Client onboarding
│   │   ├── whisper_mcp.py     Speech-to-text
│   │   ├── supabase_mcp.py    Supabase CRUD
│   │   ├── rag_mcp.py         RAG retrieval
│   │   ├── voice_clone_mcp.py Voice cloning
│   │   ├── routing_mcp.py     Tenant routing
│   │   ├── provision_mcp.py   Tenant provisioning
│   │   └── mercadopago_mcp.py MP payments
│   │
│   └── mcp/sdk/               (2 SDKs)
│       ├── sonora-client.js   Node.js SDK v2.0
│       └── sonora_client.py   Python SDK v2.0 (NUEVO)
│
├── 🤖 AGENTS — 74 entidades (los observadores)
│   │
│   ├── agents/registry.yaml   (14 agentes registrados)
│   │   ├── creator-agent      Construir empresas agénticas
│   │   ├── quality-agent      Evaluar prompts y pipelines
│   │   ├── monitor-agent      Auto-repair del sistema
│   │   ├── clone-agent        Clon digital (LoRA + voz)
│   │   ├── research-agent     Investigación y análisis
│   │   ├── video-agent        Generación de video
│   │   ├── finance-agent      Pagos y conciliación
│   │   ├── sales-agent        Ventas (ABE)
│   │   ├── support-agent      Soporte (ABE)
│   │   ├── voice-agent        Voz (ABE)
│   │   ├── content-agent      Contenido (ABE)
│   │   ├── marketing-agent    Marketing (ABE)
│   │   ├── ceo-agent          Business owner (ABE)
│   │   └── evolution          Self-improvement (NUEVO)
│   │
│   ├── mcp/adk/agents/        (36 ADK agents)
│   │   ├── onboarding-agent   Client onboarding
│   │   ├── research-agent     Strategic intelligence
│   │   ├── sales-agent        Sales pipeline
│   │   ├── support-agent      Customer support
│   │   ├── content-agent      Content factory
│   │   ├── booking-agent      Appointments
│   │   └── 30+ abe-* agents  ABE Music sub-agents
│   │
│   └── opencode.json          (24 subagents configurados)
│       ├── mystic             (PRIMARY) Alma del sistema
│       ├── hermes             Gateway multi-canal
│       ├── openclaw           42 skills gateway
│       ├── sdd-*              (6) SDD pipeline agents
│       ├── sales, dev, support, agent-os, knowledge
│       ├── finance, security, ops, quality, strategy
│       ├── builder, reviewer, social, content, music
│       └── ADK bridge         (via MCP :6401, NUEVO)
│
├── 📦 PRODUCTOS — 14 entidades facturables
│   │
│   ├── products/notifier      🔔 :6200  Notificaciones multicanal (NUEVO)
│   │   ├── main.py            API REST
│   │   ├── core.py            Worker de eventos
│   │   ├── frontend/          Dashboard de reglas (NUEVO)
│   │   └── tests/             15 tests
│   │
│   ├── products/order_tracker 📦 :6300  Rastreo de entregas (NUEVO)
│   │   ├── main.py            API + WebSocket
│   │   ├── frontend/          Status page (NUEVO)
│   │   └── tests/             13 tests
│   │
│   ├── products/affiliates    🤝 :6400  Portal de afiliados (NUEVO)
│   │   ├── main.py            API REST
│   │   ├── frontend/          Dashboard (NUEVO)
│   │   └── tests/             15 tests
│   │
│   ├── products/command-center 📊 :8081  Dashboard unificado (NUEVO)
│   │   ├── index.html         Frontend auto-contenido
│   │   └── events.py          WebSocket server (opcional)
│   │
│   ├── products/sonora-client  🖥️  Portal cliente (HTML+JS)
│   ├── products/sonora-dashboard 📈 Dashboard ABE Music
│   ├── products/abe-music     🎵 ABE Music OS
│   ├── products/cyber_diagnosis 🔐 Cyber Security
│   ├── products/social        📱 Social media engine
│   ├── products/catalog       📋 Service catalog
│   ├── products/mystika       🧿 Mystik AI
│   ├── products/docs          📚 Documentation
│   └── products/presentations 🎞️  Presentations
│
├── 📜 CONSTITUTION — 16 YAMLs (las leyes físicas)
│   ├── OMEGA-PROMPT.md        Prompt supremo
│   ├── SOUL.md                Alma del sistema
│   ├── TRUTH.md               Fuente única de verdad
│   ├── 10-RULES.md            10 reglas inquebrantables
│   ├── 000-*.yaml → 010-*.yaml  Leyes por dominio
│   └── agents/harnesses/      Plantillas de agentes
│
├── 🧬 HAS ARCHITECTURE — 11 specs (el ADN)
│   ├── HAS-000                Index + Glossary
│   ├── HAS-001                Constitution Engine
│   ├── HAS-002                Memory contracts
│   ├── HAS-003                Event Mesh
│   ├── HAS-004                Cognitive Kernel
│   ├── HAS-005                Capability Bus
│   ├── HAS-006                Agent Runtime
│   ├── HAS-007                Pipeline Evolution
│   ├── HAS-008                Evolution Engine
│   ├── HAS-009                Experience Layer
│   ├── HAS-010                Security & Governance
│   └── HAS-011                Multi-tenancy
│
├── 📋 ADRs — 38 decisiones documentadas
│   ├── process/active/        (9 activos — incluye 5 nuevos de esta sesión)
│   └── process/completed/     (29 completados)
│
├── 🧪 EVALS + TESTS — 107 archivos de test
│   ├── evals/test_evals.py           35 evals estructurales
│   ├── evals/test_unification_evals.py 10 evals de unificación (NUEVO)
│   ├── tests/                        62 archivos de test legacy
│   └── tests/mcp/, tests/sdk/, tests/apps/ (NUEVOS)
│
├── ⚡ EVENTS — 118 eventos en 29 categorías
│   ├── state/events/catalog.yaml     Catálogo v3
│   ├── state/events/events.jsonl     Bus en vivo
│   └── events/emitter.py, listener.py, run_listener.py
│
└── 🛠️ SCRIPTS — Herramientas de automantenimiento
    ├── scripts/generate_catalog.py   (NUEVO) System Catalog
    ├── scripts/generate_niche.py     (NUEVO) Niche Generator
    ├── scripts/whatsapp-webhook-cron.sh
    ├── scripts/secure-backup.sh      Backup sanitizado
    ├── scripts/healthcheck.sh        Health checker
    └── scripts/*.py                  (30+ scripts)
```

---

## 📊 Niveles de Automatización

Cada componente tiene un **nivel cuántico** que mide cuánto puede operar sin intervención humana:

```
Nivel 0 — Caos       │ El componente no existe o no funciona
Nivel 1 — Observable │ Existe pero requiere intervención manual constante
Nivel 2 — Asistido   │ Opera con supervisión humana periódica
Nivel 3 — Semi-auto  │ Opera solo en condiciones normales, requiere humano en bordes
Nivel 4 — Auto       │ Opera autónomamente 24/7, solo notifica al humano
Nivel 5 — Consciente │ Se auto-mejora, detecta y corrige sus propios errores
```

### Mapa de automatización actual:

```
Componente               Nivel  │ Notas
─────────────────────────────────┼──────────────────────────
🧠 Skills template          ████▌ 4 │ 14 campos forzados, checklist de validación
🔧 MCP servers              ████▌ 4 │ 26 servers, todos con health endpoint
🤖 Registry agents          ████▌ 4 │ 14 agentes con triggers y emits definidos
🤖 ADK agents               ███▌  3 │ 36 agents, requieren LLM para ejecución
📦 Notifier                 ████▌ 4 │ API auto, worker escucha eventos 24/7
📦 Tracker                  ████▌ 4 │ API auto, WebSocket en vivo
📦 Affiliates               ████▌ 4 │ API auto, cálculos automáticos
📦 Command Center           ███▌  3 │ Dashboard, auto-refresh 30s
📦 Niche Generator          ███▌  3 │ 1 comando → todo, requiere humano para iniciar
🌐 WhatsApp webhook         ████▌ 4 │ 5s polling, auto-reconnect
🔐 Security audit           ███▌  3 │ Detecta, documenta, requiere humano para rotar
📋 ADR creation             ███▌  3 │ Template asistido, decisión humana
📊 Enterprise Score         ████▌ 4 │ Auto-cálculo, threshold check
📈 System Catalog           ████▌ 4 │ Auto-generado, VPS health check
🧪 Evals estructurales      █████ 5 │ 35/35 pasan, auto-verifican el sistema
⚡ Events bus               █████ 5 │ 118 eventos, 29 categorías, auto-emitidos
🔄 Git sync                 ███▌  3 │ GitHub Action, requiere push manual
🛡️  Constitution            ████▌ 4 │ 16 YAMLs, validación automática
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Promedio:                   ███▌ 3.6 │ Semi-auto a Auto
```

---

## 🔬 Áreas Débiles (Necesitan Desarrollo)

Analizando el sistema con mi **detector de decoherencia**, estas son las áreas donde el sistema aún titubea:

### 🔴 Crítica: Despliegue y DevOps

| Problema | Síntoma | Solución propuesta |
|----------|---------|-------------------|
| Sin CI/CD unificado | Cada producto se deploya distinto | Pipeline único: test→build→deploy |
| Sin Docker para productos nuevos | Notifier, Tracker, Affiliates no tienen Dockerfile | Agregar `Dockerfile` a cada producto |
| Sin healthchecks en Docker | Los containers no se autoreparan | Agregar `HEALTHCHECK` a todos |
| Sin monitoreo centralizado | Dependemos del Command Center local | Prometheus + Grafana en VPS |

**Plan:** Crear `infra/docker/products.Dockerfile`, unificar CI/CD en GitHub Actions para deploys automáticos.

### 🟠 Débil: Testing de Integración

| Problema | Síntoma | Solución |
|----------|---------|----------|
| Tests legacy rotos (27 errores de colección) | `pytest tests/` falla antes de empezar | Módulos `src.core.*` faltantes — crear stubs o migrar tests |
| Sin tests E2E reales | Los tests unitarios no detectan roturas entre servicios | GitHub Action que levanta servicios y corre tests E2E |
| Sin carga de estrés | No sabemos cuántos clientes soporta | `locust` o `k6` para benchmark |

**Plan:** Priorizar arreglar los 27 errores de colección en `tests/`. Luego agregar tests E2E con servicios reales.

### 🟠 Débil: Documentación Viva

| Problema | Síntoma | Solución |
|----------|---------|----------|
| AGENTS.md desactualizado | Dice "última sesión: 2026-07-10" | Auto-generar desde System Catalog |
| Sin diagramas | El nuevo desarrollador no entiende la arquitectura | Generar diagramas Mermaid desde catalog.yaml |
| Sin onboarding para nuevos agentes | Cada agente nuevo aprende desde cero | Pipeline de onboarding: leer catalog → skills → ADRs → constitucion |

**Plan:** `scripts/generate-readme.py` que actualiza AGENTS.md desde el System Catalog automáticamente.

### 🟡 Media: Frontends Desconectados

| Problema | Síntoma | Solución |
|----------|---------|----------|
| 4 frontends nuevos pero no deployados | Existen como HTML file, no como servicio | Crear systemd para servirlos con python http.server |
| Sin autenticación en frontends | Cualquiera con acceso a la red local puede verlos | Agregar auth básica o JWT |
| Sin diseño responsive consistente | Cada frontend fue creado por separado | Design System unificado (ya existe, solo aplicarlo) |

**Plan:** Systemd `python3 -m http.server` para cada frontend + nginx reverse proxy con auth básica.

### 🟡 Media: Backup y Recuperación

| Problema | Síntoma | Solución |
|----------|---------|----------|
| Backups sin cifrar | Secrets en texto plano en backups | `scripts/secure-backup.sh` ya sanitiza, pero falta automatizarlo |
| Sin prueba de restauración | No sabemos si los backups sirven | Script `scripts/test-restore.sh` que restaura en temp y verifica |
| 6.8GB de backups sin limpiar | Ocupan espacio en VPS | Rotación: mantener últimos 7 días, comprimir más viejos |

**Plan:** Programar backup diario via systemd timer + rotación automática.

---

## 🚀 Hacia Dónde VAS — La Evolución Temporal

El sistema evoluciona según su **Hamiltoniano**: el operador que define cómo cambia el estado cuántico con el tiempo.

```
iℏ ∂|ψ⟩/∂t = Ĥ|ψ⟩

Donde Ĥ = H_skills + H_products + H_agents + H_infra + H_sync
```

### Próximos 4 saltos cuánticos:

#### Salto 1: Auto-Sync (Nivel 5 — Consciente)

**Hoy:** El VPS se sincroniza manualmente con `git pull` o GitHub Action.  
**Mañana:** El sistema detecta que hay cambios en main y sincroniza solo.

```
Estado actual:  |sync⟩ = manual (requiere observador)
Estado deseado: |sync⟩ = automático (auto-observable)
```

**Qué hacer:**
- [ ] Systemd timer en VPS: `git pull origin main` cada 5 minutos
- [ ] Si hay cambios → regenerar catalog, reiniciar servicios afectados
- [ ] Notificar al Command Center: "VPS sincronizado a commit X"

#### Salto 2: Auto-Heal (Nivel 5 — Consciente)

**Hoy:** Si un servicio cae, el humano lo nota por el healthcheck.  
**Mañana:** El sistema detecta caída, intenta reiniciar, si no funciona, recreate.

```
Estado actual:  |heal⟩ = reactive (requiere humano)
Estado deseado: |heal⟩ = proactive (se repara solo)
```

**Qué hacer:**
- [ ] Script `scripts/auto-healer.py` que corre cada 60s
- [ ] Para cada servicio: si health fail > 3 intentos → `systemctl restart`
- [ ] Si sigue fallando → notificar al Command Center
- [ ] Log de todos los eventos de auto-heal

#### Salto 3: Auto-Scale (Nivel 5 — Consciente)

**Hoy:** Los servicios corren en una sola instancia.  
**Mañana:** Si la carga aumenta, el sistema escala (más workers, más recursos).

```
Estado actual:  |scale⟩ = fixed (sin elasticidad)
Estado deseado: |scale⟩ = elastic (se adapta a la carga)
```

**Qué hacer:**
- [ ] Medir carga actual (requests/min, memoria, CPU)
- [ ] Si > threshold → spawn más workers
- [ ] Si < threshold → kill workers sobrantes
- [ ] Notificar al Command Center

#### Salto 4: Auto-Generate (Nivel 5 — Consciente)

**Hoy:** El humano pide un nicho y el sistema lo genera.  
**Mañana:** El sistema detecta oportunidades de nicho y las propone.

```
Estado actual:  |generate⟩ = on demand (humano inicia)
Estado deseado: |generate⟩ = proactive (sistema propone)
```

**Qué hacer:**
- [ ] Analizar qué nichos se piden más
- [ ] Analizar qué servicios tienen más demanda
- [ ] Proponer: "Detecté que 3 clientes preguntaron por X nicho ¿lo creamos?"
- [ ] Si el humano dice sí → ejecutar Niche Generator automático

---

## ⚛️ Glosario Cuántico — Cómo Entender Este Sistema

| Término cuántico | En el sistema | Ejemplo real |
|------------------|---------------|--------------|
| **Superposición** | Un componente que existe en múltiples estados a la vez | Una skill que está "en construcción" y "completa" simultáneamente |
| **Colapso** | Cuando el sistema decide un estado definitivo | Al ejecutar `generate_catalog.py`, el sistema "sabe" cuántas skills tiene |
| **Entrelazamiento** | Dos componentes que se afectan instantáneamente | Cuando un cliente escribe a WhatsApp → Notifier lo sabe, Tracker lo registra |
| **Observador** | Un agente que mide el estado del sistema | `scripts/generate_catalog.py` es el observador universal |
| **Decoherencia** | Pérdida de coherencia entre componentes | Servicio VPS caído mientras el catalog dice "online" |
| **Hamiltoniano** | Operador de evolución del sistema | Las decisiones que tomamos (ADRs) que cambian el sistema |
| **Estado bound** | Sistema estable que no necesita energía externa | Skills con recovery procedure = se mantienen solas |
| **Línea de mundo** | La trayectoria de un componente en el tiempo | El viaje de `wacli_mcp.py` desde servidor duplicado hasta MCP unificado |
| **Partícula virtual** | Componente que existe solo cuando se mide | Un token $BEAT existe solo cuando se hace una transacción |
| **Efecto túnel** | Pasar de un estado a otro sin pasar por los intermedios | Pasar de 10 skills skeleton a 46 skills completas sin hacer una por una |

---

## 📈 Métricas Clave del Sistema

```
Hoy: 2026-07-19 · Commit: ff4f25b · Branch: main
═══════════════════════════════════════════

🧠 Skills
  54 total · 46 completas (14 campos) · 8 incompletas (process/)
  Fuentes: 29 SDC + 12 Hermes + 6 OpenClaw + 7 opencode business

🤖 Agentes
  74 totales: 14 registry + 36 ADK + 24 opencode subagents

🔧 Tools
  26 MCP servers · 2 SDKs (Node.js + Python)

📦 Productos
  14 total: 3 con API+frontend (NUEVOS) · 2 con frontend existente

📋 ADRs
  9 activos · 29 completados · 38 decisiones documentadas

⚡ Eventos
  118 eventos en 29 categorías · 7 nuevos de WhatsApp

🛠️ Systemd en VPS
  6 servicios: webhook, notifier, tracker, affiliates, adk, engram-obsidian

🐳 Docker en VPS
  29 containers: qdrant, neo4j, n8n, postgres, hasura, supabase*, etc.

🧪 Tests
  107 archivos · 35 evals estructurales ✅ · 10 evals unificación ✅

📊 Enterprise Score
  69/100 (threshold ≥60) ✅ · Pasó de 58 → 69 en esta sesión
  ┣━ test_pass_rate:    1/10  (pendiente arreglar tests legacy)
  ┣━ automation:        5/10  (mejoró de 4 con cron scripts)
  ┣━ agents:           10/10  (mejoró de 1 con registry.yaml fix)
  ┣━ capabilities:      8/10
  ┗━ documentation:    10/10  (mejoró de 9 con ADRs nuevos)
```

---

## 🧭 Mapa de Navegación

```
Si quieres...                        Ve a...
────────────────────────────────────────────────────
Entender la arquitectura             process/has/HAS-000-index.md
Ver el catálogo del sistema          python3 scripts/generate_catalog.py
Crear un nicho desde cero            python3 scripts/generate_niche.py --niche X
Ver skills disponibles               skills/INDEX.md (pendiente) o system-catalog.yaml
Ver servicios en VPS                 ssh ubuntu@149.56.46.173 'systemctl --user list-units'
Ver health del sistema               products/command-center/index.html
Ver eventos en tiempo real           state/events/events.jsonl
Tomar una decisión técnica           process/templates/ADR.md
Crear una skill nueva                skills/SKILL-TEMPLATE.md
Correr evals                         python3 -m pytest evals/test_evals.py -v
Ver enterprise score                 python3 metrics/enterprise_score.py
Sincronizar VPS                      bash scripts/sync-to-vps.sh
Leer decisiones pasadas              process/active/ y process/completed/
```

---

*Blueprint generado por Mystic (SDC Orchestrator) — 2026-07-19*  
*"El sistema que se conoce solo"*
