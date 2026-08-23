# BLUEPRINT — Sonora Digital Corp (SDC) v0.12.0
**Fecha**: 2026-08-23 | **Sesión**: SDD-0012 Rediseño Web Chat + Voz Pro Max  
**Commit**: `next` branch (producción) | **VPS OVH**: 149.56.46.173 (sdc-prod)

---

## 1. VISIÓN GENERAL DEL SISTEMA

Sonora Digital Corp (SDC) es una **plataforma multi-tenant de asistentes IA conversacionales** para PyMEs.  
**Identidad**: *No vendemos tecnología, devolvemos tiempo.*  
Cada cliente tiene su propio agente (tenant aislado) que atiende 24/7 por Web/Telegram/WhatsApp con voz (STT/TTS) y agenda citas con confirmación audio por WhatsApp.

### Principios Rectores (Constitution)
| # | Principio | Implementación |
|---|-----------|----------------|
| I | Orquestación única | Hermes gateway :8642 (bots/canales) + vps_ai_server :8643 (chat+voz) |
| II | Separación Determinista vs LLM | Routing, scoring, agenda = determinista; conversación = LLM + SOUL |
| III | Cargas pesadas SOLO en VPS | STT/TTS/LLM corren en OVH 149.56.46.173; laptop = terminal |
| IV | Testing TDD | 22/22 tests PASS (SDD-0012) |
| V | Trazabilidad | Engram + SQLite + logs JSON |

---

## 2. ARQUITECTURA DE ALTO NIVEL

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USUARIOS (Web/Telegram/WhatsApp)            │
└──────────────────────────┬──────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CLOUDFLARE TUNNEL (sonoradigitalcorp.com)       │
│  TLS termination + WAF + DDoS protection                            │
└──────────────────────────┬──────────────────────────────────────────┘
                           ▼
              ┌────────────┴────────────┐
              ▼                         ▼
┌───────────────────────┐   ┌───────────────────────┐
│  NGINX VPS :80/443    │   │  NGINX VPS :80/443    │
│  Static assets        │   │  /api/* → :8643       │
│  /var/www/...         │   │  /webhook/* → :5291   │
└───────────────────────┘   └───────────────────────┘
              │                         │
              ▼                         ▼
┌───────────────────────┐   ┌───────────────────────┐
│ vps_ai_server :8643   │   │ hermosillo-webhook :5291│
│ • /api/v1/chat/completions│   │ Telegram webhook      │
│ • /api/stt (proxy→:5292)│   │ Onboarding Nathaly    │
│ • /api/tts (proxy→:5293)│   │                       │
│ • /api/v1/citas       │   │                       │
│ • /health             │   │                       │
└───────────┬───────────┘   └───────────────────────┘
            │
     ┌──────┼──────┐
     ▼      ▼      ▼
┌──────┐ ┌──────┐ ┌──────┐
│ STT  │ │ TTS  │ │ LLM  │
│:5292 │ │:5293 │ │OpenR │
└──────┘ └──────┘ └──────┘
     │      │      │
     └──────┼──────┘
            ▼
    ┌─────────────────┐
    │   VPS OVH       │
    │ 149.56.46.173   │
    │ 11GB RAM        │
    │ Ollama :11434   │
    │ Qdrant :6333    │
    │ SQLite/Engram   │
    └─────────────────┘
```

---

## 3. COMPONENTES CORE

### 3.1 UI Pro Max — Web Chat (`chat_pro_max/index.html`)
**Single-file SPA** con:
- **Three.js r128**: Orbe 3D IcosahedronGeometry (2562 verts) + 520 partículas GPU, shader fresnel reactivo a audio
- **Glassmorphism**: `backdrop-filter: blur(24px) saturate(150%)`, bordes 1px rgba(255,255,255,.14)
- **Chat**: Virtual list, streaming tokens, burbujas glass, auto-scroll 60fps
- **Mic push-to-talk**: MediaRecorder → `/api/stt` (webm/opus) → texto → chat
- **TTS playback**: `<audio>` + AnalyserNode → orb pulse visual + botón STOP
- **Comando silencio**: regex `SILENCE_RE` detecta "calla/silencio/basta/quita la voz"
- **Catálogo 8 nichos**: Cards horizontales Netflix-style con ahorros $/mes + "Ver en acción"
- **Agenda visible**: Modal 10 días hábiles + 8 slots → POST `/api/v1/citas` → TTS + wacli WhatsApp
- **Personas**: `?p=sdc` (azul/dorado) | `?p=nathaly` (verde) — rebrandea hero, colores, WA, voz
- **Cero dashboard**, **cero signos exclamación**, **beneficios-first copy**

**Endpoints consumidos**:
| Endpoint | Método | Uso |
|----------|--------|-----|
| `/api/v1/chat/completions` | POST | Chat streaming |
| `/api/stt` | POST multipart | Voz → texto |
| `/api/tts` | GET/POST | Texto → MP3 |
| `/api/v1/citas` | POST | Agendar + audio WhatsApp |

---

### 3.2 vps_ai_server.py — Backend Unificado (`:8643`)
**Archivo**: `01_Core_Platform/04_Automations_and_Workflows/vps_ai_server.py` (aiohttp)

| Endpoint | Función | Modelo/Engine |
|----------|---------|---------------|
| `POST /api/v1/chat/completions` | Chat con SOUL inyectado server-side | **Primary: nemotron-3-ultra-free** (eval 83%) → fallback deepseek-0731 |
| `POST /api/stt` | Proxy → STT server :5292 | faster-whisper small int8 |
| `GET/POST /api/tts` | Proxy → TTS server :5293 | edge-tts (Dalia/Jorge) |
| `POST /api/v1/citas` | Agenda + TTS confirm + wacli WhatsApp | TTS + wacli 0.12.0 |
| `GET /health` | Estado agregado stt+tts+llm | Check interno |

**SOUL Server-Side** (determinista, no depende del LLM):
- Inyecta system prompt por `person` (sdc/nathaly) con reglas duras
- `clean_reply()`: quita `!¡`, colapsa puntos, **corta a 320 chars en frase completa** (crítico para TTS)
- `soft_replace_tech()`: defensa en profundidad anti-palabras técnicas
- `max_tokens: 220` (optimizado para respuestas breves)

**Chain de modelos (EVAL OPTIMIZADO)**:
```python
MODEL_CHAIN = [
    "nvidia/nemotron-3-ultra-550b-a55b:free",  # primary: rápido, gratis, 83% pass
    "deepseek/deepseek-v4-flash-0731",          # fallback: pago
]
```

---

### 3.3 Voice Stack VPS (STT/TTS)

| Servicio | Puerto | Tech | Systemd Unit | RAM/CPU |
|----------|--------|------|--------------|---------|
| **STT** | 5292 | faster-whisper small int8, beam_size=3, initial_prompt es-MX | `sdc-stt.service` | ~500MB |
| **TTS** | 5293 | edge-tts (es-MX-DaliaNeural/JorgeNeural), clean_for_tts | `sdc-tts.service` | ~50MB |
| **LLM Proxy** | 8643 | vps_ai_server (aiohttp) | `vps-ai-server.service` | ~100MB |

**wacli 0.12.0** (Go binary): `/home/mystic/.local/bin/wacli`  
Store: `/home/mystic/.wacli` (AUTHENTICATED=true, JID 5216623538272)  
Keepalive: `wacli-keepalive.service` (`sync --follow`, Restart=always)

---

### 3.4 Hermes Gateway (`:8642`)
**Archivo**: `~/.hermes/hermes-agent/gateway/run.py`  
**Systemd**: `hermes-gateway.service` (user, Linger)  
**Función**: Orquestador único de bots/canales (Telegram, WhatsApp, email)  
**Config**: `~/.hermes/config.yaml` → `deepseek/deepseek-v4-flash-0731` (legacy)  
**Multi-tenant**: `tenant_router.py` + `tenants.json` + `agents_registry.json`

---

### 3.5 Multi-Tenant Agents (`~/.hermes/agents/`)
Cada agente = un Hermes dedicado:
| Agente | Tenant | Nicho | Modelo | Canales |
|--------|--------|-------|--------|---------|
| `nathaly` | hermosillo-cont | Contabilidad | nemotron-free | telegram, web |
| `comercial-flexible` | sonora-digital-corp | hibrido | nemotron-free | telegram, whatsapp, web |
| `soporte-adaptado` | sonora-digital-corp | hibrido | nemotron-free | telegram, whatsapp, web |
| `asistente-hibrido` | sonora-digital-corp | hibrido | nemotron-free | telegram, whatsapp, web |

**Agent structure**:
```
~/.hermes/agents/<id>/
├── agent.yaml        # metadata (modelo, skills, composio, canales)
├── persona.md        # QUIÉN es (recepcionista/comercial/doctor/policia)
├── reglas.md         # límites y reglas operativas
├── manual.md         # procedimientos
├── skills/           # capacidades reutilizables
└── tools/            # tools custom
```

**MCP Server**: `hermes_agents_mcp.py` (tools: list_agents, agent_info, agent_shell, agent_persona, agent_rules, composio_available)

---

### 3.6 Onboarding Engines (Deterministas)

| Engine | Tenant | Archivo | DB |
|--------|--------|---------|----|
| Aztrotech | aztrotech | `onboarding_engine.py` + `lead_scoring.py` + `lead_intelligence.py` | `leads_aztrotech.db` + `lead_intelligence_aztrotech.db` |
| Hermosillo | hermosillo-cont | `onboarding_hermosillo.py` + `lead_classifier_hermosillo.py` | `leads_hermosillo_cont.db` |

**Scoring cold/warm/hot** (determinista, reusa `lead_scoring.py`):
- COLD <40, WARM 40-69, HOT ≥70
- Factores: datos básicos (30pts), intención (25), urgencia/autoridad (25), engagement (20)

---

### 3.7 Prompt Registry (Gobernanza)
```
prompt_registry/
├── eval_prompts.yaml      # 6 casos, expect_benefits, must_not
├── run_eval.py            # call_llm con retries, juez determinista + LLM
└── specs/                 # Gherkin/BDD + TDD (por caso)
```
**Pipeline**: Spec (SDD) → Gherkin → TDD → Generación → Eval → SPEC JUDGE (nemotron-free)

---

## 4. INFRAESTRUCTURA VPS (OVH 149.56.46.173)

| Servicio | Puerto | Systemd Unit | Estado |
|----------|--------|--------------|--------|
| NGINX | 80/443 | nginx.service | ✅ active |
| Cloudflare Tunnel | — | cloudflared-tunnel.service | ✅ active |
| Hermes Gateway | 8642 | hermes-gateway.service | ✅ active |
| vps_ai_server | 8643 | vps-ai-server.service | ✅ active |
| STT Server | 5292 | sdc-stt.service | ✅ active |
| TTS Server | 5293 | sdc-tts.service | ✅ active |
| Hermosillo Webhook | 5291 | hermosillo-webhook.service | ✅ active |
| Ollama | 11434 | (docker) | ✅ active |
| wacli keepalive | — | wacli-keepalive.service | ✅ active |

**RAM VPS**: 11GB total, ~10GB libre (1.2GB usado)  
**Ollama modelos**: all-minilm (384-dim embeddings), qwen3:4b, qwen2.5  
**Qdrant**: Colecciones por tenant (kb_*, tenant_*) 384-dim Cosine

---

## 5. BASES DE DATOS

| DB | Ubicación | Tablas clave |
|----|-----------|--------------|
| `citas_{persona}.db` | `/opt/hermes/citas_db/` | `citas(id, persona, nombre, negocio, telefono, fecha, hora, estado)` |
| `leads_aztrotech.db` | `~/.openclaw/workspace/` | `leads`, `lead_intelligence_aztrotech` |
| `leads_hermosillo_cont.db` | `Databases/` | `leads` (scoring, clasificación) |
| `leads_hermosillo_cont.db` | `Databases/` | `lead_intelligence` (resumen, objeciones, next_action) |
| Engram | `~/.engram` | Memoria persistente cross-sesión |

---

## 6. SKILLS CLAVE (Reutilizables)

| Skill | Ubicación | Uso |
|-------|-----------|-----|
| `sdc-wacli` | `~/.hermes/skills/sdc/sdc-wacli/` | Enviar WhatsApp voz/texto |
| `sdc-tts-local` | `~/.hermes/skills/sdc/sdc-tts-local/` | TTS Kokoro/edge |
| `sdc-voice-pipeline` | `~/.hermes/skills/sdc/sdc-voice-pipeline/` | STT+TTS pipeline |
| `landing-dinamica-cliente` | `.opencode/skills/mystic/landing-dinamica-cliente/` | Plantilla landing + widget voz |
| `plantilla-cliente-ia` | `.opencode/skills/mystic/plantilla-cliente-ia/` | Provisioning tenant completo |
| `spec-judge` | `.opencode/skills/mystic/spec-judge/` | SPEC JUDGE para prompts |
| `aztrotech-citas` | `~/.hermes/skills/clients/aztrotech-citas/` | Protocolo citas Aztrotech |
| `telegram-tenant-router` | `~/.hermes/skills/sdc/telegram-tenant-router/` | Sync tokens Telegram por tenant |

---

## 7. GITHUB ACTIONS CI/CD (Pendiente de activar)

Ver sección **GitHub Actions** abajo.

---

## 8. MEMORIA PERSISTENTE (Engram)

**Proyecto**: `sonora-digital-corp`  
**Scope**: `project`  
**Keys importantes**:
- `sdd-0012-web-chat-voice` — arquitectura decision
- `sdd-0012-eval-prompts` — eval decision (nemotron primary)
- `sdd-0004-aztrotech-onboarding` — onboarding engine
- `sdd-0006-hermosillo` — onboarding Nathaly
- `sdd-0012-web-chat-voice-redesign` — blueprint session

---

## 9. DESPLIEGUE (Deploy Checklist)

```bash
# 1. Deploy código a VPS
scp -i ~/.ssh/id_ed25519_sdc <files> ubuntu@149.56.46.173:/opt/hermes/
scp -i ~/.ssh/id_ed25519_sdc index.html ubuntu@149.56.46.173:/var/www/sonoradigitalcorp/

# 2. Restart services
ssh sdc-prod 'sudo systemctl restart vps-ai-server sdc-stt sdc-tts nginx'

# 3. Verificar health
curl https://sonoradigitalcorp.com/health
curl https://sonoradigitalcorp.com/ | grep -c "orb3d\|catalogRail\|agendaBtn"
```

---

## 10. TESTING MATRIX

| Test Suite | Archivo | Casos | Estado |
|------------|---------|-------|--------|
| SDD-0012 Unit/Integración | `test_sdd0012_web_chat.py` | 22 | ✅ PASS |
| Eval Prompts | `run_eval.py` | 6 casos × 2 modelos | ✅ nemotron 83% |
| Onboarding Aztrotech | `test_aztrotech_onboard.py` | 28 | ✅ PASS |
| Onboarding Hermosillo | `onboarding_hermosillo.py` tests | 9 | ✅ PASS |

---

## 11. CONFIGURACIÓN LOCALES (Laptop)

**Laptop = Solo terminal** (3.3GB RAM, cero procesos pesados):
- OpenCode + SSH a VPS
- wacli local (`~/.local/bin/wacli`) para tests
- Engram local (`~/.engram`) synced via mem_save
- `.opencode/` config + skills

---

## 12. ROADMAP / PRÓXIMOS PASOS

| Prioridad | Item | Esfuerzo |
|-----------|------|----------|
| Alta | Kokoro ONNX es-MX para TTS local (0 tokens) | Medio |
| Alta | FAL_KEY regenerar (generar imágenes catálogo) | Bajo |
| Media | LinkedIn en Composio (actualmente solo IG+GitHub) | Bajo |
| Media | Eval prompts programado (cron semanal) | Bajo |
| Baja | Dashboard multi-tenant César/Mystic | Alto |

---

*Generado automáticamente: 2026-08-23 | SDD-0012 v1.0 | Commit: `next`*