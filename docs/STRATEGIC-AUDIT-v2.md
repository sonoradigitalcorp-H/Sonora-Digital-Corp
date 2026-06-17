# SONORA DIGITAL OS — TOTAL SYSTEM DISCOVERY & STRATEGIC AUDIT v2

> Basado exclusivamente en evidencia encontrada. Sin asunciones. Sin inventar capacidades.

---

# FASE 1: SYSTEM DISCOVERY

## ¿Qué está intentando construir?

Sonora Digital Corp intenta construir **una plataforma multi-agente B2B** que crea y opera trabajadores digitales autónomos (Digital Clones, AI Employees, AI Receptionists, etc.) sobre una infraestructura de agentes, memoria vectorial, bases de datos de grafos y automatizaciones.

La visión documentada es **SONORA DIGITAL OS** — una "fábrica escalable de trabajadores digitales".

## ¿Qué productos existen?

| Producto | Estado | Evidencia |
|----------|--------|-----------|
| **ABE Music** | ⚠️ Experimental | Data JSON (57KB), script daemon corriendo, hub frontend en `/projects/ABE-MUSIC-HUB/`, bot en TypeScript, landing HTML. **Sin entregables al cliente.** |
| **SDC Business** | 📄 Código | `sdc_business.py` con planes (Explorador/Conquistador) y lógica CRM. **Sin clientes.** |
| **Mysticverse** | 📄 Código | `mysticverse.py` con DigitalTwinPipeline. **Sin clones digitales reales.** |
| **SDC Shop** | 📄 Datos | `store-products.json`, `store-orders.json` (0 órdenes). |
| **Zamora (cliente)** | 📄 Data | `zamora.json` (2KB), landing HTML. **Sin entregables.** |
| **AzREC** | 📄 Data | En carpeta products/azrec. **Sin implementación.** |

## ¿Qué MVPs existen?

- **Orquestador de agentes** (`orchestrator.py`, 430 líneas) — Funcional, enruta tareas a 12+ agentes especializados
- **Web UI** (`main.py`, sirve en puerto 5174) — Dashboard funcional, **28 páginas HTML estáticas** en webui/static/
- **Hermes API** (Docker, puerto 8000) — API backend funcional, health check ✅
- **Publisher Service** (`services/publisher/server.py`) — FastAPI para multi-platform publishing, **nunca llamado**
- **Thumbnail Generator** (`services/thumbnails/server.py`) — FastAPI para generar thumbnails, **nunca llamado**
- **n8n** — Docker configurado, 1 workflow exportado (newsjacking JSON), **no corre**

## ¿Qué módulos existen?

### Core (Activos)
- `orchestrator.py` — Enrutamiento de tareas a agentes
- `engram.py` — Memoria persistente SQLite + FTS5
- `brain_graph.py` — Grafo de conocimiento Neo4j
- `chunker.py` — Chunking de documentos
- `verify.py` — Verificación de outputs
- `sdc_business.py` — Planes, CRM lite, onboarding
- `mysticverse.py` — Digital twin pipeline (código, no operativo)
- `unified_bridge.py` — Bridge entre sistemas
- `mcp_connectors.py` — Conectores MCP (6 servidores configurados)

### Agents (12 especializados, en `src/core/agents/`)
`HermesAgent`, `OpenClawAgent`, `CodeAgent`, `ExploreAgent`, `ResearchAgent`, `MemoryAgent`, `SkillAgent`, `VoiceAgent`, `ReviewAgent`, `PRAgent`, `GbrainAgent`, `VerifyAgent`

### Tests (376 tests, 33 archivos)
Cobertura en: voice, agents, brain_graph, chunker, embeddings, engram, orchestrator, mysticverse, sdc_business, payments, security, rag, tools, verification, ABE music, bridge.

## ¿Qué está abandonado?

- **Prometheus/Grafana** — Docker containers exited (9 días caídos)
- **n8n** — No corre, workflows no activos
- **CI/CD** — systemd service `cicd.service` inactivo (dead)
- **Sync VPS** — Cron `sync_vps.sh` corre cada 8h pero no hay VPS
- **Social automation** — `social_automation.py` corre cada 4h pero no hay evidencia de posts reales
- **Playwright E2E** — Tests existen, monitor HDMI configurado, no hay evidencia de uso continuo
- **Mobile app** — Solo README.md
- **Especs archivados** — 26 specs archivadas de ~36 totales

## ¿Qué está activo?

**Infraestructura**: 5 Docker containers ✅ | 7 systemd services ✅ | 15 cron jobs ✅
**Monitoreo**: healthchecks cada 15min ✅ | ABE daemon cada 10min ✅ | alertas de disco/RAM ✅
**JARVIS UI**: Sirviendo en puerto 5174 ✅
**OpenClaw Gateway**: Sirviendo en puerto 18789 ✅
**Memorias**: 43 en engram principal, 304 observaciones en otro DB
**Tests**: 376 tests, pasan ✅
**Skills**: 42 OpenClaw skills + 5 JARVIS skills + 21 Hermes skill categories

---

# FASE 2: ECOSYSTEM INVENTORY

## Frontend

**Stack real:** HTML estático + CSS vanilla + JS vanilla. **No hay React, Next.js, Vue, Svelte, Astro, Tailwind, Framer Motion, Three.js activos.** El package.json solo tiene Playwright como dependencia.

**Páginas estáticas (28 en webui/static/):**
- SDC Landing, SDC Portal, SDC Products, Sonora main
- ABE Music, ABE Dashboard, ABE System, ABE Report
- Zamora, Zamora System
- Mysticverse Hub, Agency Control, Blueprint Presentation
- Wakeup, New UI, Quantum Reflection, Brain Dashboard
- 100 Questions, Brand Images, QR Proxy
- Night Ops (3 variantes), Report, Reporte Ecosistema
- Presentation, Abe Reporte Ejecutivo

**Dashboard activo:** JARVIS UI en puerto 5174 (HTML servido por FastAPI).

## Backend

**Stack real:** Python (FastAPI) — **No hay Node.js, Go, Express, GraphQL.**

| Servicio | Puerto | Status |
|----------|--------|--------|
| Hermes API (FastAPI) | 8000 | ✅ Running |
| JARVIS Core (FastAPI) | 5174 | ✅ Running |
| OpenClaw Gateway | 18789 | ✅ Running |
| Publisher Service | 8001 | ❌ No responde |
| Thumbnail Generator | 8002 | ❌ No responde |

## Infrastructure

| Componente | Estado | Notas |
|------------|--------|-------|
| Docker (5 containers) | ✅ | hermes_api, infra_postgres, jarvis-qdrant, infra_redis, jarvis-neo4j |
| Docker Compose | ✅ | `docker-compose.yml` + `docker-compose.automation.yml` |
| Systemd (7 servicios) | ✅ | JARVIS Core, Hermes Gateway, OpenClaw Gateway, Sonora Publisher, Sonora Thumbnails, GitHub Runner, JARVIS UI |
| No VPS | ❌ | Hostinger Premium Web Hosting. No hay VPS. |
| No Reverse Proxy | ❌ | No Nginx, no Traefik, no Caddy |
| No HTTPS local | ❌ | Todo corre en HTTP plano, localhost |

## Data Layer

| Base de datos | Uso real | Estado |
|--------------|----------|--------|
| **SQLite (Engram)** | Memoria del agente, 43 entries | ✅ Activo |
| **Neo4j** | Grafos de conocimiento | ✅ Activo (puerto 7474/7687) |
| **Qdrant** | Embeddings vectoriales, 1 colección (`jarvis_knowledge`) | ✅ Activo |
| **Postgres (Hermes)** | Datos de Hermes Agent | ✅ Activo (puerto 5432) |
| **Redis** | Caché/colas | ✅ Activo (puerto 6379) |
| **Filesystem JSON** | store-products.json, store-orders.json, abe-music.json, zamora.json | ⚠️ Datos estáticos |

## AI Layer

| Proveedor/Modelo | Uso | Estado |
|-----------------|-----|--------|
| **DeepSeek V4 Flash** | Modelo principal via OpenRouter | ✅ En uso |
| **OpenRouter** | API gateway para LLMs | ✅ Configurado en `.env` |
| **FAL AI** | Generación de imágenes | ✅ API key en `.env` |
| **Edge-TTS / gTTS / Whisper** | Voz | ✅ En requirements.txt |
| **Qdrant embeddings** | RAG | ✅ Funcional, 1 colección |
| **No Ollama / local models** | — | ❌ No detectado |

## Agent Layer

| Agente | Propósito | Estado |
|--------|-----------|--------|
| **HermesAgent** | Orquestador principal con gateway de mensajería | ✅ Systemd activo |
| **OpenClawAgent** | Acceso a skills y herramientas | ✅ Gateway activo |
| **CodeAgent** | Generación de código | 📄 Código listo |
| **ExploreAgent** | Exploración de codebase | 📄 Código listo |
| **ResearchAgent** | Investigación | 📄 Código listo |
| **MemoryAgent** | Gestión de memoria | 📄 Código listo |
| **VoiceAgent** | Voz TTS/STT | 📄 Código listo |
| **ReviewAgent** | Code review | 📄 Código listo |
| **SkillAgent** | Gestión de skills | 📄 Código listo |
| **PRAgent** | Pull requests | 📄 Código listo |
| **GbrainAgent** | Brain graph | 📄 Código listo |
| **VerifyAgent** | Verificación | 📄 Código listo |
| **SDC Business Agent** | CRM/Planes | 📄 Lógica en sdc_business.py |

**Ningún agente opera autónomamente 24/7 fuera del ABE daemon.** Todos dependen de ser invocados.

## MCP Layer

| Servidor | Transporte | Estado |
|----------|-----------|--------|
| hermes | remote | ✅ Configurado |
| openclaw | remote | ✅ Configurado |
| jarvis-bridge | remote | ✅ Configurado |
| qdrant | remote | ✅ Configurado |
| neo4j | remote | ✅ Configurado |
| n8n | remote | ⚠️ n8n no corre |

## Automation Layer

**n8n:** No corre. Workflows exportados existen en `automation/n8n-workflow-newsjacking.json`.

**Cron (15 jobs):**
- ✅ memory-save.py (cada hora)
- ✅ backup (3 AM diario)
- ✅ healthcheck (cada 15 min)
- ✅ self-improve (cada 6h)
- ✅ behavior-analyzer (cada 6h)
- ✅ disk/RAM alerts
- ✅ night-ops-update (cada 15 min)
- ✅ ABE report push (lunes 9 AM)
- ✅ ABE delivery gate (lunes 9:30 AM)
- ⚠️ social_automation (cada 4h — sin evidencia de posts)
- ⚠️ sync_vps (cada 8h — no hay VPS)
- ❌ CI/CD pipeline (dead)

**No hay webhooks, no hay triggers automáticos, no hay event-driven automation corriendo.**

---

# FASE 3: BUSINESS CAPABILITY ANALYSIS

| Capacidad | Estado | Evidencia |
|-----------|--------|-----------|
| **WhatsApp Automation** | ❌ Roto | QR proxy existe, bridge configurado en opencode MCP, pero no hay evidencia de mensajes enviados/recibidos |
| **Telegram Automation** | ❌ Roto | Bot ABE existe en TypeScript en ABE-MUSIC-HUB, no corriendo |
| **CRM** | 📄 Parcial | Lógica en `sdc_business.py`, 0 clientes, 0 leads |
| **Lead Capture** | ❌ No existe | Sin formularios, sin landing activa, sin integración |
| **Appointment Booking** | ❌ No existe | Sin calendarizador, sin integración |
| **AI Chat** | ⚠️ Parcial | Hermes API responde pero no hay chat público expuesto |
| **Voice AI** | 📄 Experimental | Dependencias instaladas, agente voice.py existe, sin despliegue activo |
| **Knowledge Base** | ✅ Operativo | Qdrant + Neo4j + Engram, RAG funcional |
| **Digital Clone** | 📄 Experimental | `DigitalTwinPipeline` en `mysticverse.py`, nunca ejecutado |
| **Multi-Agent Systems** | ✅ Operativo | Orchestrator con 12 agentes, enrutamiento funcional |
| **Sales Automation** | ❌ No existe | Sin pipeline de ventas automatizado |
| **Customer Support** | ❌ No existe | Sin ticket system, sin chatbot de soporte |
| **Content Creation** | ⚠️ Parcial | FAL AI para imágenes, content pipeline esqueleto, social_manager.py existe |
| **Internal Operations** | ⚠️ Parcial | Monitoreo ✅, backups ✅, reportes 📄 |
| **SDC Shop** | 📄 Parcial | Data estática, 0 órdenes, sin checkout real |

---

# FASE 4: USER EXPERIENCE AUDIT

**Realidad:** 28 páginas HTML estáticas, diseño oscuro consistente, sin framework UI.

- **Responsive:** ❌ No probado. Páginas usan CSS básico.
- **Mobile First:** ❌ No. Diseñado para desktop.
- **Performance:** ✅ Rápido (HTML estático, sin JS pesado).
- **Accessibility:** ❌ No evaluado. Sin ARIA, sin contraste verificado.
- **Design Consistency:** ⚠️ Consistente visualmente (tema oscuro, azul/neón) pero sin design system.
- **Onboarding:** ❌ No existe flujo de onboarding.
- **Personalization:** ❌ No existe.
- **Three.js / WebGPU / Interactive Avatars:** ❌ No hay nada de esto. Solo HTML estático.
- **AI-driven UX:** ❌ No hay UI reactiva basada en IA.

---

# FASE 5: PRODUCTIZATION AUDIT

## ¿Puede venderse actualmente?

### Para Músicos (ABE Music)
- **Barreras:** Sin demo funcional, sin onboarding, sin dashboard de cliente, sin entregables al cliente actual (ABE), sin canal de ventas.
- **Riesgos:** ABE lleva 162 ciclos de daemon sin recibir un solo reporte. Si el cliente pide ver resultados, no hay nada que mostrar.
- **Faltantes:** Portal cliente, automatización de reportes, generación de contenido real, integración con distribución digital.

### Para Creadores
- **Barreras:** Sin landing pública, sin producto definido, sin canal de adquisición.
- **Riesgos:** El concepto "Digital Clone" no está implementado. El código existe pero nunca se ejecutó.
- **Faltantes:** MVP funcional de clone, portal de gestión, pricing claro.

### Para Negocios Locales
- **Barreras:** Sin CRM, sin lead capture, sin appointment booking.
- **Riesgos:** Competidores (GoHighLevel, ManyChat) tienen producto completo. SDC tiene 0.
- **Faltantes:** Embudo de ventas completo, WhatsApp automation funcional, integración con calendario.

### Para Agencias
- **Barreras:** Sin white label, sin multi-tenancy, sin API pública.
- **Riesgos:** Producto demasiado inmaduro para revender.
- **Faltantes:** API documentada, dashboard de agencia, facturación.

### Para Empresas
- **Barreras:** Sin SSO, sin seguridad enterprise, sin SLA.
- **Riesgos:** Infraestructura en laptop personal sin backup externo.
- **Faltantes:** Despliegue cloud, seguridad, monitoreo.

---

# FASE 6: TECHNICAL DEBT REPORT

| Deuda | Impacto | Prioridad |
|-------|---------|-----------|
| **sync_vps.sh corriendo cada 8h** — No hay VPS | Bajo | 🟡 Media |
| **CI/CD service dead** | Alto | 🔴 Alta |
| **Prometheus/Grafana exited 9 days** | Medio | 🟡 Media |
| **Publisher service no responde** | Medio | 🟡 Media |
| **Thumbnail service no responde** | Bajo | 🟢 Baja |
| **n8n no corre** | Alto | 🔴 Alta |
| **social_automation.py corre sin evidencia de posts** | Medio | 🟡 Media |
| **2 Engram DBs (jarvis/engram.db y ~/.engram/engram.db)** | Medio | 🟡 Media |
| **Archivos sueltos en raíz**: funcion.py, funcion_ejemplo.py, funcion_analisis.py, saludo.py, mi_funcion.py, ejemplo_funcion.py, funcion_python.py | Bajo | 🟢 Baja |
| **26 specs archivadas vs 10 activas** | Medio | 🟡 Media |
| **specs.old/ y specs-archive/ duplicados** | Bajo | 🟢 Baja |
| **node_modules/ en JARVIS repo** | Bajo | 🟢 Baja |
| **2 Docker images no usadas** (grafana, prometheus) | Bajo | 🟢 Baja |

---

# FASE 7: FUTURE SONORA DIGITAL OS ARCHITECTURE

Basado exclusivamente en lo encontrado:

## Conservar
- **Orquestador de agentes** — Base sólida, 12 agentes, extensible
- **Engram** — Memoria unificada, funcional
- **Qdrant + Neo4j** — Stack vectorial + grafos, potente
- **Hermes Gateway** — Bridge de mensajería, funcional
- **376 tests** — Base de calidad
- **42 OpenClaw skills** — Catálogo de capacidades
- **Docker infra** — Postgres, Redis, Qdrant, Neo4j

## Eliminar
- **sync_vps.sh** — No hay VPS
- **specs.old/ y specs-archive/** — Contenido duplicado
- **Archivos sueltos en raíz** — Basura
- **Prometheus/Grafana containers** — No se usan
- **node_modules/** — No necesario en repo

## Fusionar
- **2 Engram DBs** → 1 sola `~/.engram/engram.db` (parcialmente hecho)
- **ABE-MUSIC-HUB repo** → Integrar en JARVIS como módulo de cliente
- **Publisher + Thumbnail services** → Simplificar, no merecen servicios separados

## Reemplazar
- **n8n** → O revivir con workflows reales o reemplazar por scripts Python/cron
- **Static HTML** → Framework real (React/Svelte) si se necesita UX interactiva
- **Sin reverse proxy** → Agregar Nginx/Caddy cuando haya tráfico externo

## Escalar
- **WhatsApp/Telegram bridges** — De código a operación real
- **Digital Twin pipeline** — De clase Python a servicio ejecutable
- **CRM** — De lógica embebida a sistema con leads reales

---

# FASE 8: MASTER SYSTEM MAP

```
USERS
  │
  ├─► Browser ──► JARVIS UI (FastAPI :5174)
  │                   │
  ├─► WhatsApp ──► Hermes Gateway (:18789) ──► Hermes API (:8000)
  │                                                    │
  ├─► Telegram ──► [Bot Caído]                         │
  │                                                    │
  └─► API ──► OpenClaw Gateway                         │
                                                       │
              ┌─────────────────────────────────────────┘
              ▼
    JARVIS Core Orchestrator (systemd)
              │
              ├─► 12 Specialized Agents
              │       ├─► CodeAgent
              │       ├─► ExploreAgent
              │       ├─► ResearchAgent
              │       ├─► MemoryAgent
              │       ├─► VoiceAgent
              │       └─► ... (7 more)
              │
              ├─► MCP Layer
              │       ├─► hermes (remote)
              │       ├─► openclaw (remote)
              │       ├─► jarvis-bridge (remote)
              │       ├─► qdrant (remote)
              │       ├─► neo4j (remote)
              │       └─► n8n (remote — caído)
              │
              ├─► Data Layer
              │       ├─► Engram (SQLite + FTS5)
              │       ├─► Neo4j (graph :7687)
              │       ├─► Qdrant (vectors :6333)
              │       ├─► Postgres (:5432)
              │       └─► Redis (:6379)
              │
              ├─► Services (systemd)
              │       ├─► sonora-publisher (FastAPI :8001 — caído)
              │       └─► sonora-thumbnails (FastAPI :8002 — caído)
              │
              ├─► Cron (15 jobs)
              │       ├─► memory-save (hourly)
              │       ├─► backup (daily 3AM)
              │       ├─► healthcheck (15min)
              │       ├─► self-improve (6h)
              │       ├─► social_automation (4h)
              │       └─► ... (10 more)
              │
              ├─► Clients
              │       ├─► ABE Music (único cliente pagando)
              │       │       ├─► daemon (10min cycles)
              │       │       ├─► bot (TypeScript — no corre)
              │       │       ├─► data JSON (57KB)
              │       │       └─► 7 landing pages estáticas
              │       │
              │       ├─► Zamora (sin actividad)
              │       └─► AzREC (sin actividad)
              │
              └─► Products (0 paying users)
                      ├─► SDC Shop (0 orders)
                      ├─► Mysticverse (no ejecutado)
                      └─► Digital Twin (no ejecutado)
```

---

# FASE 9: TRUTH REPORT

## ✅ Lo que funciona realmente

1. **Infraestructura base**: 5 Docker containers, 7 systemd services, 15 cron jobs — todo estable
2. **Orquestador de agentes**: Enruta tareas a 12+ agentes especializados
3. **376 tests**: Base de pruebas sólida, pasan todas
4. **Monitoreo**: Healthchecks, backups, alertas de disco/RAM
5. **Memoria**: Engram funcional con búsqueda FTS5
6. **Vector store**: Qdrant con colección de conocimiento
7. **Graph DB**: Neo4j operativo
8. **Web UI**: Sirviendo 28 páginas estáticas + dashboard

## ⚠️ Lo que parece funcionar pero no

1. **ABE Music daemon** — Corre cada 10 minutos pero **solo monitorea RAM**. No genera reportes, no envía entregables. El cliente paga $3,000/mes y recibe 0 valor.
2. **Social automation** — Corre cada 4 horas pero **no hay evidencia de posts publicados** en ninguna plataforma.
3. **Self-improve** — Corre cada 6 horas, logs muestran actividad pero sin métricas de mejora tangible.
4. **CI/CD** — Service está "dead", no hace test/commit/push automático.
5. **Publisher + Thumbnail services** — Systemd los reporta como "active" pero los puertos no responden.

## 🤥 Lo que es humo

1. **Digital Clone / Digital Twin** — Existe la clase `DigitalTwinPipeline` en código. Nunca se ejecutó. No hay un solo clon digital funcionando.
2. **SDC Shop** — `store-products.json` y `store-orders.json` existen pero `store-orders.json` tiene 0 órdenes. No hay checkout, no hay carrito, no hay pagos reales.
3. **n8n** — Configurado en MCP, workflow exportado, pero el container no corre. No hay automatización visual.
4. **Multi-platform publishing** — Publisher service no responde. No hay videos publicados en YouTube/TikTok/Instagram.
5. **WhatsApp bridge** — QR proxy existe, pero no hay evidencia de mensajes fluyendo.
6. **CRM** — `sdc_business.py` tiene lógica de planes y clientes. Cero clientes registrados.
7. **Mysticverse** — Código completo de pipeline de contenido adulto. Sin uso real.
8. **26 specs archivadas** — Documentación de intenciones pasadas. No representan capacidades actuales.

## 🟢 Lo que es MVP (mínimo viable funcional)

1. **JARVIS Orchestrator** — 12 agentes, enrutamiento funcional, extensible
2. **Hermes API** — Backend funcional con health check
3. **Memory/Knowledge stack** — Engram + Qdrant + Neo4j integrados
4. **Test suite** — 376 tests, cobertura en módulos clave
5. **OpenClaw skills** — 42 skills instaladas y configurables

## 🔴 Lo que está listo para clientes

**Nada.** Literalmente nada puede venderse mañana.

- ABE Music es el único cliente y no está recibiendo servicio
- No hay landing pública cargando
- No hay formulario de registro/contacto
- No hay sistema de pagos funcional
- No hay onboarding
- No hay dashboard de cliente
- No hay canal de ventas

## Lo que puede venderse mañana

**Nada.** El sistema tiene la **infraestructura** para construir productos, pero ningún producto está en estado "vendible".

## Lo que requiere reconstrucción

1. **Estrategia de producto** — Definir QUÉ se vende exactamente y a QUIÉN
2. **Canal de ventas** — LinkedIn, cold email, o lo que sea — pero necesita existir
3. **ABE Music delivery** — El cliente pagante debe recibir algo esta semana
4. **Landing pública** — Subir a Hostinger, que cargue, que tenga un CTA
5. **WhatsApp/Telegram funcional** — Canales de comunicación con clientes
6. **Lead capture** — Mínimo: formulario + notificación + seguimiento
7. **Onboarding mínimo** — Qué pasa cuando alguien dice "quiero comprar"

---

# FASE 10: EXECUTIVE CTO RECOMMENDATION

Si entro como CTO por 90 días, sabiendo que la prioridad es **Revenue > Productization > Stability > Scalability > Customer Experience**:

## Semana 1: Detener la hemorragia

**Día 1-2: Salvar ABE Music**
- Generar el primer reporte ejecutivo para ABE Music usando los datos en `abe-music.json`
- Enviarlo por el canal que el cliente use (WhatsApp/Email)
- Programar recurrencia semanal
- ***Impacto: $3,000/mes retenidos vs riesgo de cancelación***

**Día 3: Podar lo muerto**
- Eliminar `sync_vps.sh`, archivos basura en raíz, containers de Prometheus/Grafana
- Matar crons que no sirven (social_automation si no tiene outputs)
- ***Impacto: Reducción de ruido, el systemd deja de reportar falsos positivos***

**Día 4-5: Subir la landing a Hostinger**
- No más diseño. Subir el HTML que ya existe.
- Verificar que sonoradigitalcorp.com cargue con HTTPS.
- Agregar un formulario simple (botón de WhatsApp o email link).
- ***Impacto: Presencia web pública → credibilidad → leads***

## Semana 2: Activar canales

**Día 6-7: Revivir WhatsApp**
- Depurar el WhatsApp bridge hasta que envíe/recriba mensajes
- Conectar con Hermes Gateway
- **Prueba: enviar un mensaje desde el celular y que JARVIS responda**
- ***Impacto: Canal de comunicación con clientes operable***

**Día 8-9: Revivir n8n o reemplazarlo**
- Opción A: Arrancar n8n, importar workflow, verificar
- Opción B: Reemplazar con script Python + cron (más simple, más barato)
- Crear un workflow real: "Si llega un lead por la web → notificar → guardar en JSON"
- ***Impacto: Automatización real, no documentación***

**Día 10: Dashboard de ABE Music**
- El cliente pagante necesita ver su data
- Usar una de las 28 páginas HTML estáticas como dashboard funcional
- Conectar con datos reales de `abe-music.json`
- ***Impacto: Retención de cliente + caso de éxito para vender***

## Mes 1: Productizar 1 cosa

**Semana 3-4: Definir UN producto y venderlo**
- Elegir UNO: ABE Music OS (el que ya paga) como producto flagship
- Definir: nombre, precio, qué incluye, qué no
- Preparar: landing de producto + propuesta comercial + onboarding
- ***Regla: NO construir nada que un cliente no haya pedido***

**Semana 5-6: Pipeline de ventas**
- 10 outreach por día en LinkedIn a dueños de sellos/músicos
- Script: "Así ayudamos a ABE Music con [resultado concreto]"
- Cada conversación → lead en JSON → seguimiento automático
- ***Métrica: 10 leads/semana → 1 llamada/semana → 1 cierre/quincena***

**Semana 7-8: Onboarding + delivery**
- Cuando alguien dice "sí": onboarding en 24h
- Checklist: configurar bot, cargar data, primer reporte, primera interacción
- ***Objetivo: Tener 3 clientes pagando $1,000-3,000/mes cada uno***

## Mes 2: Escalar lo que funciona

- Automatizar el onboarding (que sea 80% automático)
- Dashboard de cliente real (con datos vivos, no HTML estático)
- Si ABE Music está feliz: pedir referidos, caso de estudio, testimonio
- Segundo producto: AI Receptionist para negocios locales (si hay demanda)
- ***Métrica: $10k MRR***

## Mes 3: Sistema → Plataforma

- Si hay 5+ clientes: estandarizar la "fábrica de trabajadores digitales"
- Documentar el proceso de clone/employee/receptionist
- Invertir en infraestructura real (VPS, dominio, SSL)
- Contratar si es necesario (o delegar a JARVIS)
- ***Métrica: $15-20k MRR, sistema repetible, 3 casos de éxito***

---

## Resumen de 5 acciones inmediatas

| # | Acción | Por qué | Tiempo |
|---|--------|---------|--------|
| 1 | **Entregar reporte a ABE esta semana** | $3,000/mes en riesgo | 2 horas |
| 2 | **Subir landing a Hostinger** | Presencia web = 0 → 1 | 1 hora |
| 3 | **Podar sync_vps.sh + containers muertos** | Ruido → señal | 30 min |
| 4 | **Revivir WhatsApp bridge** | Canal de comunicación | 1 día |
| 5 | **Elegir 1 producto y empezar a venderlo** | Revenue > todo | 1 semana |

> **La verdad:** Tienes infraestructura de sobra para construir un negocio real. Lo que falta no es tecnología. Es enfoque en una sola cosa, entrega al cliente que ya tienes, y alguien vendiendo. Los 42 skills, 12 agentes, 376 tests, 5 containers, 7 services, 15 cron jobs, 28 páginas — todo eso no vale nada si no hay un cliente recibiendo valor. Empieza por ABE. Esta semana.
