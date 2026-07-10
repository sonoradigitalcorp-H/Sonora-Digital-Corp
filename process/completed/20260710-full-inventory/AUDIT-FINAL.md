# AUDITORÍA FINAL — Sonora Digital Corp
> 2026-07-10 | 5 auditorías paralelas | 759 tests

---

## 1. RESEARCH: MEJORES PROMPTS (GitHub + HuggingFace)

### Fuentes principales encontradas
| Recurso | Stars | Para qué sirve |
|---------|-------|----------------|
| `f/prompts.chat` | 165k | Librería de prompts + MCP server + CLI + self-hostable |
| `dair-ai/Prompt-Engineering-Guide` | 76.3k | Guía completa (técnicas, agentes, context engineering) |
| `asgeirtj/system_prompts_leaks` | 55.5k | System prompts reales de Claude/GPT/Gemini/Grok/Copilot |
| `alirezarezvani/claude-skills` | 22k | 345 agent skills/plugins para 8+ coding agents |
| `langfuse/langfuse` | 30.9k | Prompt management + evals + observabilidad |
| `promptfoo/promptfoo` | 23.1k | Testing de prompts/agents/RAG en CI/CD |

### Técnicas a adoptar YA
1. **ReAct** (Reason+Act) — patrón core para agentes
2. **Layered Context Architecture** — System/Task/Tool/Memory layers
3. **Meta-prompting** — prompts que mejoran prompts
4. **Few-shot con selección dinámica** — Active-Prompt
5. **Context Engineering** — constraints explícitos, errores, escalación

### Dataset de prompts en HuggingFace
- `fka/prompts.chat` — 34.9k descargas (misma librería)
- `yatin-superintelligence/White-Hat-Security-Agent-Prompts-600K` — 600k prompts de seguridad
- `HuggingFaceH4/mt_bench_prompts` — 8k prompts benchmark

---

## 2. AUDITORÍA MCP

### ✅ Funcionando
- **MCP Gateway** (:18989) — 188 tools expuestas, JWT auth, 4 HTML dashboards
- **Hermes MCP** (:8000) — health endpoint `/health` responde OK
- **OpenClaw Gateway** (:18789) — health endpoint `/health` responde live
- **33 tool modules** en `mcp/tools/`
- **Skill registry** + **Capability registry** funcionales
- **7 workflows** YAML válidos (100%)
- **Docker**: 13 containers running (Neo4j, Qdrant, n8n, Postgres, Redis, etc.)

### 🔴 Roto
| Problema | Severidad | Fix |
|----------|-----------|-----|
| **24/36 ADK agent YAMLs** tienen error de indentación (1 espacio vs 2) | **ALTA** | Fix de indentación en línea 10 |
| **Hermes health tool** apunta a `/api/hermes/health` (404) en vez de `/health` | **ALTA** | Cambiar endpoint en `hermes.js` |
| **OpenClaw `/skills`** devuelve 404 | **MEDIA** | Fix en OpenClaw gateway |
| **Metabase MCP** (:3002) no corre | **BAJA** | Iniciar o eliminar config |
| **Paperclip MCP** (:3100) tiene otro proceso | **BAJA** | Revisar qué corre ahí |
| **capability-registry.js** apunta a path que no existe | **MEDIA** | Actualizar path |

### ❌ No existe
- **Hermes Doctor** — no hay ningún módulo doctor/hermes
- **OpenClaw Doctor** — no hay ningún módulo doctor/openclaw
- **MCP stdio gateway** — `mcp-gateway.js` no corre como proceso

---

## 3. AUDITORÍA DE EVENTOS

### Estado del event bus
| Métrica | Valor |
|---------|-------|
| Eventos en `catalog.yaml` | **57** (23 categorías) |
| Eventos emitidos en código real | ~40+ tipos |
| Eventos en `events.jsonl` | **522 eventos, 56 tipos** |
| Eventos en capabilities YAML (no catalogados) | ~30+ adicionales |
| Eventos en catalog NO usados | ~25 (ej: `plan.*`, `code.*`, `build.*`, `deploy.*`) |
| Eventos en código NO catalogados | ~45+ |
| Archivos procesados | **1** (test estático — no hay pipeline real) |

### 🔴 Problemas críticos
1. **Catalog.yaml está obsoleto** — solo ~12/57 eventos se usan realmente
2. **Eventos de capabilities no están en catalog** — 8 capabilities definen ~30 eventos propios
3. **No hay pipeline de procesamiento** — `processed/` tiene 1 archivo test estático
4. **Dual schema** — `events.jsonl` mezcla formato legacy (`event:`) y HAS-003 (`type:`)
5. **No hay routing** — no hay subscriber registry; todo es archivo plano

### Endpoints API descubiertos
- **Total**: ~160+ endpoints en todas las apps
- **webui**: ~90 endpoints (chat, MCP, payments, sales, voice, webhooks, sessions, skills, store, brain, content)
- **abe-service**: ~30 endpoints (REST + WS)
- **guardian**: 11 endpoints
- **control**: 5 endpoints
- **brain**, **hermes**, **understand**: ~3-5 c/u

### Webhooks configurados
- 7 app-level (n8n-backup, n8n-healthcheck, whatsapp, payments)
- ~12 n8n workflows con webhooks
- Dominio: `n8n.sonoradigitalcorp.com`

---

## 4. AUDITORÍA DE INFRAESTRUCTURA

### DNS
| Dominio | SSL | Estado |
|---------|-----|--------|
| `sonoradigitalcorp.com` | ✅ Let's Encrypt | Activo |
| `api.sonoradigitalcorp.com` | ✅ Let's Encrypt | Activo |
| `n8n.sonoradigitalcorp.com` | ✅ Let's Encrypt | Configurado |
| `app.sonoradigitalcorp.com` | ✅ Monitoreado | Activo |
| `music.sonoradigitalcorp.com` | ✅ Monitoreado | Activo |
| `soulclone.sonoradigitalcorp.com` | ✅ Monitoreado | Activo |
| `mystika.sonoradigitalcorp.com` | ❌ `ssl: false` | Sin SSL |

### SSL
- Let's Encrypt via Certbot
- HSTS habilitado (2 años)
- TLSv1.2 + TLSv1.3
- Monitoring de expiry via Telegram alerts
- ⚠️ `mystika.sonoradigitalcorp.com` no tiene SSL

### CI/CD (26 GitHub Actions)
| Workflow | Trigger | Función |
|----------|---------|---------|
| `ci.yml` | Push/PR | Tests Python + ruff |
| `deploy.yml` | Push main | Build + deploy Docker |
| `sync-vps.yml` | Push main | Git pull en VPS |
| `monitor.yml` | hourly+daily | Health check completo |
| `backup.yml` | Weekly Mon | pg_dump + gzip |
| `security.yml` | Weekly Mon | CodeQL + safety + npm audit |
| `process-gate.yml` | PR | Enterprise Score ≥60, Constitution |
| `mcp-gateway.yml` | Push/PR mcp/ | ADK + tools tests |
| `vercel-deploy.yml` | Push frontends/ | Vercel deploy |
| +17 más... | | |

### Sync
- Dual: GitHub Action (`sync-vps.yml`) + rsync directo (`scripts/sync-to-vps.sh`)
- Cron: git pull cada hora, scrapers cada 6h

### Docker
- **Core** (11 servicios): postgres, redis, neo4j, qdrant, mcp-server, n8n, telegram-bot, langfuse, langfuse-db, jarvis-webui, jarvis-core
- **Products** (3 servicios): content-server, omnivoice, open-notebook
- **No Docker** (systemd): abe-service, kernel, guardian, evolucion-dashboard, hermes-gateway, openclaw, mystika-web/api/bot

### Backup
- 6 niveles: diario (cron 3AM) → volumes → sanitized → GH Action → autonomous → SQLite
- 8 backups existentes (~160MB total)
- ⚠️ Sin backup off-site (todo local en VPS)

### Monitoring
- Telegram alerts cada 15min (disk, memory, services, SSL, fail2ban)
- Healthcheck cada 15min (Docker detect→diagnose→recover→retest)
- Prometheus + Grafana configurados (no verificado si corre)
- Autonomous script cada 15min (health + recovery + reports)

---

## 5. AUDITORÍA DE ESTRUCTURA

### 🔴 Duplicados críticos (7 pares)
| Par | Acción |
|-----|--------|
| `apps/learn/` ↔ `apps/learning/` | Eliminar `apps/learning/` |
| `apps/measure/` ↔ `apps/agent_metrics/` | Eliminar `apps/agent_metrics/` |
| `apps/abe-service/` ↔ `apps/abe_service/` | Eliminar `apps/abe_service/` |
| `infra/n8n/` ↔ `config/n8n-sdc/` | Eliminar `infra/n8n/` |
| `collectors/` ↔ `scrapers/` | Fusionar en `collectors/` |
| `frontends/docs/` ↔ `docs/` | Fusionar en `docs/` |
| `mcp/tools/` ↔ `tools/` | Documentar relación |

### Archivos huérfanos en root
- 6 archivos `.env*` → mover a `config/`
- `sdc-architecture-blueprint.html` → mover a `docs/`
- 12 archivos sueltos en `products/` raíz → mover a subdirectorios

### Directorios vacíos (25+)
- `state/business/`, `state/content-queue/`, `state/files/`, `state/media/`, etc.
- `agents/architect/`, `agents/builder/`, `agents/evolution/`, etc.
- `evolution/metrics/`, `evolution/proposals/`

### Archivos temporales
- `apps/_test_write_temp.txt`, `apps/jarvis/_test_write_temp.txt`
- `products/.~lock.*` (LibreOffice)
- 85 archivos de log en `state/logs/audit/auto-heal-*.log`

### Inconsistencias de naming
| Inconsistencia | Ejemplo |
|----------------|---------|
| kebab-case vs snake_case en scripts | `memory-save.py` vs `social_automation.py` |
| `abe_service` vs `abe-service` | Ambos coexisten |
| `collectors/` vs `scrapers/` | Misma función, 2 directorios |

---

## 6. SDKs, ADKs, AGENT MDS, LIBRERÍAS

### SDK
- `mcp/sdk/sonora-client.js` — ✅ Existe, cliente MCP para Node.js
- ❌ No hay SDK para Python

### ADK
- `mcp/adk/adk.js` — ✅ Adapter implementado
- `mcp/adk/agents/` — 36 YAMLs (12 válidos, 24 rotos por indentación)
- `mcp/adk/agents/abe-*.yaml` — 24 ABE agent definitions con YAML inválido

### Agent MDs
- `AGENTS.md` — ✅ 360 lines, actualizado
- `agents/registry.yaml` — ✅ 11 agentes registrados
- `agents/capabilities/` — ✅ 8 capabilities definidas
- `agents/policies/` — ✅ 7 policies (deny-all)
- `mcp/adk/agents/` — ⚠️ 24 YAMLs rotos

### Librerías principales
| Runtime | Package Manager | Key Dependencies |
|---------|----------------|-----------------|
| Python 3.14 | pip (externally-managed) | fastapi, uvicorn, pydantic, yaml, httpx, neo4j, qdrant-client |
| Node.js | npm | express, http, fs |
| Docker | docker-compose | 14 containers |

---

## 7. RESUMEN: QUÉ NO ESTÁ UNIDO / QUÉ ESTÁ VOLANDO

### No está conectado
| Sistema A | Sistema B | Lo que falta |
|-----------|-----------|--------------|
| **Capability Bus** (nuevo) | **Capability Registry** (mcp/registry/) | No integrados — el bus no consulta el registry |
| **Observe (L1)** | **Understand (L2)** | Funcionan pero no hay pipeline automático L1→L2 |
| **Events** | **Event Processing** | 522 eventos acumulados sin procesar |
| **Hermes health** | **Correct endpoint** | Apunta a URL que devuelve 404 |
| **ADK agents** | **ADK runtime** | 24/36 YAMLs rotos, no cargables |
| **backups** | **off-site storage** | Todo local, nada en S3/B2 |
| **collectors/** | **scrapers/** | Misma función, 2 directorios |
| **mcp/tools/** | **tools/** (docs) | Implementación vs documentación separadas |
| **apps/agents/** | **apps/act/agents/** | Re-export frágil (mocks rotos antes del fix) |
| **nginx.conf** (Docker) | **nginx-vps.conf** | Diferentes paths de SSL |

### Está volando (sin dueño/clasificación)
| Archivo/App | Problema |
|-------------|----------|
| `webui/` (root) | Directorio residual, contenido mínimo |
| `self-heal/` | Scripts sueltos, deberían estar en `scripts/` |
| `prompts/prompts/` | Anidamiento innecesario (`prompts/` dentro de `prompts/`) |
| `apps/data/` | Datos de store dentro de apps |
| `clients/logs/` | Logs dentro de clients/ |
| 12 archivos HTML sueltos en `products/` | Sin subdirectorio de producto |
| `infra/server.py` | Python file suelto en infra/ |
| `capabilities/bus.py` (legacy) | Stub, reemplazado por `capabilities/bus/` |
| `metrics/enterprise_score.py` | Script en metrics/ (aceptable pero suelto) |

---

## 8. RECOMENDACIONES PRIORIZADAS

### Hágalo ahora (30 min)
1. ✅ Fix 24 ADK agent YAMLs (indentación)
2. ✅ Fix Hermes health tool endpoint (`/api/hermes/health` → `/health`)
3. ✅ Eliminar archivos temp (`_test_write_temp.txt`, `.~lock.*`)
4. ✅ Arreglar capability-registry.js path

### Hágalo hoy (2-4 horas)
5. Fusionar `apps/learning/` → `apps/learn/`
6. Eliminar `apps/abe_service/` (duplicado)
7. Eliminar `infra/n8n/` (duplicado de `config/n8n-sdc/`)
8. Mover archivos `.env*` de root a `config/`
9. Mover HTMLs sueltos de `products/` a subdirectorios
10. Actualizar `catalog.yaml` con eventos reales

### Hágalo esta semana
11. Consolidar `collectors/` y `scrapers/`
12. SSL para `mystika.sonoradigitalcorp.com`
13. Backup off-site (restic → B2/S3)
14. Consolidar `frontends/` y `apps/webui/`
15. Python SDK para MCP
16. Pipeline de procesamiento de eventos (L1→L2 automático)
17. Integrar Capability Bus con Capability Registry

### Hágalo este mes
18. Implementar Orquestrador de Eventos (consumer registry)
19. Multi-tenancy (HAS-011)
20. 7-layer memory system completo
21. Actualizar prompts con técnicas ReAct + Context Engineering
22. Consolidar naming: decidir kebab-case o snake_case
23. Limpiar directorios vacíos
