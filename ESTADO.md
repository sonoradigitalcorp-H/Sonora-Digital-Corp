# ESTADO VIVO (se actualiza con /mejora — leer SIEMPRE al arrancar)

- Producción: VPS 187.124.85.191, usuarios Nathaly/Marco/TripleR activos, CI/CD despliega desde main.
- Repo: rama `master` local; GitHub remoto `sonoradigitalcorp-H/Sonora-Digital-Corp`. Rama `next` pendiente de crear/pushear (main intocada).
- **Modelo LLM (2026-08-12)**: `deepseek/deepseek-v4-flash-0731` vía OpenRouter en `~/.hermes/config.yaml` + `config.json`. Key OpenRouter activa en ~/.hermes/.env. Ollama VPS OVH (149.56.46.173) disponible para embeddings ($0). Verificar créditos antes de asumir fallo.
- Engram: v1.19.0, plugin opencode instalado (memoria persistente entre sesiones). 
- OpenCode COSUDE: AGENTS.md + ESTADO.md + /idea /validar /mejora /contexto + @orquestador @clientes @redes @voz + skill estilo-mystic. Reiniciar opencode para cargar.
- **HERMES = ÚNICO ORQUESTADOR (2026-08-12)**: OpenClaw ELIMINADO (npm + systemd user). Gateway `hermes-gateway.service` (systemd user, Linger) en `127.0.0.1:8643` (HTTP 200). Modelo `deepseek/deepseek-v4-flash-0731`. Bots cesar/rye pendientes de configurar en Telegram de hermes.
- **⚠️ PC 3.3GB RAM — REGLA DE ORO**: Cero procesos pesados en local. LLM y embeddings pesados → VPS OVH (149.56.46.173) o OpenRouter. Conocimiento de OpenClaw migrado a `~/.hermes/skills/` (clients/cesar-*, clients/rye-*, sdc-*) y respaldado en `~/.hermes/scripts/migrated/` (openclaw.json.respaldo, identity.py, identity_resolver.py, tenant_router.py).
- **Embeddings DUAL (2026-08-10)**: Ollama LOCAL activo (systemd `ollama.service`, enable --now, 127.0.0.1:11434) con `all-minilm:latest` (45.9MB, 384-dim). VPS OVH `149.56.46.173:11434` (docker) con all-minilm (384-dim) + qwen3:4b + qwen2.5. Script embedding usa `OLLAMA_ENDPOINT` (de ~/.hermes/.env = VPS). Qdrant local 6333 con colecciones por tenant: kb_rye, kb_aztrotech, hermes, tenant_aztrotech (384 dims, Cosine). ⚠️ all-minilm local INSTALADO (2026-08-10).
- Clientes a activar: Aztrotech, ABE Music Group. RYE (Iván Guerrero) bot ActivoGo/RyE_production_bot, Aztroc_Assistant (cesar).
- Voice Clone César: Assets listos → Audio WAV (108s), 9 fotos → pipeline voice_cloner.py + image_cloner.py esperando XTTS/FAL para entrenar modelos. Sin XTTS instalado, usar TTS genérico (es-MX-JorgeNeural) mientras.
- **Voz SIMPLE funcionando (sin XTTS)**: script `01_Core_Platform/03_Agentic_Infrastructure/voice_reply.py` hace texto→edge-tts→OGG→Telegram sendVoice en 1 comando. Probado OK en @Aztro_tech_bot y @RyE_production_bot. Voz real de César enviada al chat para comparar. Skill voice-delivery creado.
- Landing Page Onboarding: Generada en 04_Deployment/onboarding/index.html (Three.js + branding Aztrotech). Botón WhatsApp + Web.
- Pipeline Auto-Deploy: auto_deploy.py + scripts media ready. Ejecutar cuando se instale XTTS o se configures FAL_KEY para voice/image cloning.
- Redes: playwright dry-run con fotos pendiente.
- Pendiente crítico: Nginx → /panel/login, login devuelva 200.
- Guardianes: pre-commit + structure_guard.sh (esqueleto canónico).
- **⚠️ PC 3.3GB RAM — REGLA DE ORO**: Cero procesos pesados en local. LLM (qwen3:4b) y embeddings → VPS OVH (149.56.46.173). Si la PC se congela: `free -m` (RAM<400MB = crítico), kill duplicados openclaw (`ss -tlnp | grep 18789`), swap 2.3GB = swap-thrash. **GUARDIA AUTOMÁTICO**: `01_Core_Platform/04_Automations_and_Workflows/memory-guard.sh` (cron */5) mata duplicados + MCP accesorios. NO crear procesos pesados nuevos en local.
- **Embeddings DUAL (2026-08-10)**: Ollama LOCAL activo (systemd `ollama.service`, enable --now, 127.0.0.1:11434) con `all-minilm:latest` (45.9MB, 384-dim). VPS OVH `149.56.46.173:11434` (docker) con all-minilm (384-dim) + qwen3:4b + qwen2.5. Script embedding usa `OLLAMA_ENDPOINT` (de ~/.hermes/.env = VPS). Qdrant local 6333 con colecciones por tenant: kb_rye, kb_aztrotech, hermes, tenant_aztrotech (384 dims, Cosine). ⚠️ all-minilm local INSTALADO (2026-08-10).
- **MCP server movido (2026-08-10)**: `skills/mcp/servers/sdc_mcp_stdio.py` (deriva en raíz) → `01_Core_Platform/03_Agentic_Infrastructure/MCP_Servers/sdc_mcp_stdio/`. Test integration → `03_Sandbox_and_RnD/tests/integration/`. Launcher Antigravity → `~/.local/share/applications/`. `citas.db` vacío borrado. Structure guard VERDE.
- **INFRAESTRUCTURA VIGENTE (2026-08-12)**: `hermes-gateway.service` (systemd user, Linger, puerto 8643) es el único gateway activo. Los servicios `openclaw-gateway`, `multi-tenant-bot`, `hermes-mcp`, `sdk-runtime` fueron ELIMINADOS (stack OpenClaw / rutas muertas). `wacli-gateway.service` conservado disabled (mensajería ligera local, permitida). Mantenimiento auto: `~/cron/mantenimiento-auto.sh` (diario 6:30). Auto-limpieza de Hermes habilitada.
- **REGLAS CANÓNICAS (2026-08-12)**: (1) nunca modelos pesados locales; (2) toda carga pesada (MCP, fastmcp, gateway run, npx/uvx, LLM) → VPS OVH 149.56.46.173 o proveedor remoto, NUNCA local sin conectar VPS; (3) reconocer sesión al iniciar; (4) analizar raíz y mover lo fuera de lugar (structure_guard.sh); (5) OpenClaw eliminado, solo Hermes.
- **PERSONAS / BDS (2026-08-12)**: Índice de personas consolidado `~/.hermes/tenants/people_index.py` (quien es, por nombre/número/chat_id/empresa). Registries: `people.json` + `tenants.json`. Mapa de BDs: `databases.json`. Skill `people-recognition`. Personas: Luis (dueño, +5216623538272, @sonora_digital_bot), César (5738935134, Aztrotech), Iván (rye, Cheese Assistant), leads Luisa (6623334455, Cafetería Central) y Ana en citas.db. Aislar memoria por tenant.
- **AGENTES MULTI-NICHO (2026-08-12)**: Esqueleto `~/.hermes/agents/` — un Hermes por persona/cliente. Cada agente: `agent.yaml` (metadata: nicho/modelo/skills/composio/limites), `persona.md` (personalidad: recepcionista/consultorio/doctor/policia/comercial), `reglas.md`, `manual.md`, `skills/` (capacidades reutilizables), `tools/`. Factory: `hermes_agent_factory.py` (genera agente desde orden natural vía OpenRouter 0731). Registry: `agents_registry.json` (agentes: consultorio-sonora, cesar, rye). MCP: `hermes_agents_mcp.py` (server stdio, tools: list_agents, agent_info, agent_rules, agent_persona, agent_shell, composio_available) — registrado en config hermes como mcp_server. Skills = capacidades compartidas; persona.md = personalidad única por agente.
- **COMPOSIO INTEGRADO (2026-08-12)**: Composio = cimiento de tools para agentes (gmail, googlecalendar, whatsapp, telegram, crm). Key en `~/.composio/agent.json` (cuenta happy-lantern-hare, COMPOSIO_API_KEY). Cada agente declara `composio.toolkits`. Conecta bajo demanda (sin proceso pesado local). La factory asigna toolkits automáticamente por nicho.
- **PAQUETE DE VENTAS WEB (2026-08-12)**: sonoradigitalcorp.com (nginx root /home/mystic/www). Páginas nuevas: `paquetes.html` (Starter $799 / Business $1,499 / Enterprise $3,999 + CTAs WhatsApp), `agentes.html` (agentes por nicho: consultorio, recepción, industrial, comercial, música, a medida), `chat.html` (widget de chat IA del bot). Index actualizado con nav a Agentes/Paquetes + botón flotante 🤖 de chat. API del bot expuesta en `/api/v1/` → proxy nginx a `127.0.0.1:8643/v1/` (api_server del gateway, key `API_SERVER_KEY` en ~/.hermes/.env, rate limit api 30r/m). Chat completions model deepseek/deepseek-v4-flash-0731.
- **REDES SOCIALES AUTO (2026-08-12)**: `~/.hermes/agents/social_autopilot.py` — publica en Instagram (Composio, conexión ACTIVE) y genera imagen con fal.ai (`--plan "prompt"`). FB: NO aparece en conexiones de esta cuenta composio (solo IG + github) — conectar FB para activar. FAL_KEY en ~/.hermes/.env da **401 (vencida)** — regenerar en fal.ai/dashboard para generar imágenes. Verificar: `python3 ~/.hermes/agents/social_autopilot.py --check`.
- **SPEC 0003 — STACK v3 (2026-08-12)**: `00_Administration/ADRs/0003-stack-v3-hermes-orquestador.md`. Hermes = ORQUESTADOR (gateway 8643, bots, cron). Hermes Desktop = puerta (modo api → 8643, reconectado). OpenCode = COMPONENTE de desarrollo (edita/ejecuta; no orquesta ni decide arquitectura). Composio = tools externas en el stack. Modelo 0731. Todo pesado → VPS. Pendientes: FB en composio, FAL_KEY vencida, QR WhatsApp, token Aztro_tech_bot.
- **HERMOSILLO CONTABILIDAD (2026-08-15)**: Proyecto cliente Nathaly. SDD 0006 aprobado (`01_Core_Platform/09_CICD_Pipelines/Specs/SDD/0006-hermosillo-contabilidad-bot.md`). F0 completo: tenant `hermosillo-cont` (tenants.json, tenant_router.py, people.json), agente `nathaly` (~/.hermes/agents/nathaly/, agents_registry.json), OKF servicios sin precios (`hermosillo-cont.servicios.json`), token `TELEGRAM_HERMOSILLOCONT_TOKEN` en ~/.hermes/.env. Motor determinista `onboarding_hermosillo.py` + tests 9/9 PASS. Clasificador `lead_classifier_hermosillo.py` testeado 5/5 con nemotron free. F1 (webhook bot) en curso, F2 (DNS/SSL/orbe) pendiente, F3 (dashboard CRM) pendiente. Subdominio: `NatContability.sonoradigitalcorp.com` → IP laptop 187.245.97.214 (port-forward pendiente de verificar).
- **HERMOSILLO SUPERPOWERED + VPS 24/7 (2026-08-16)**: Webhook UPGRADED `telegram_webhook_hermosillo.py` nivel senior devops: onboarding PROACTIVO (propone servicios + assets visuales + preguntas de calificación), voz DaliaNeural (edge-tts→ffmpeg→OGG→sendVoice), WhatsApp dual (empresa 6623498589 Business autenticado en `~/.config/wacli/nathaly_business/` + personal 6622681111 jefa), seguridad (rate limit 30/h + prompt injection INJECTION_RE + sanitización), scoring determinista, nota de voz al cliente para confirmar citas, notificación a jefa con voz. MODELOS: nemotron free (clasificación), deepseek fallback, edge-tts Dalia. **DESPLEGADO 24/7 EN VPS OVH**: webhook `:5291` con supervisor `/tmp/hermes/supervisor_hermosillo.sh`, nginx VPS expone `/webhook/` → 5291 y `/hermosillo.html` (orbe), Telegram `setWebhook` → `https://sonoradigitalcorp.com/webhook/<token>` ✅ E2E verificado. VPS deps: venv `/tmp/hermes/venv` (pydantic/requests/edge-tts/pytz), config `/tmp/hermes/`, DB copiada. **Proceso local DETENIDO** (el VPS opera 24/7). NOTA: `proxy_pass http://127.0.0.1:5291` sin trailing slash para preservar `/webhook/<token>`.
- **PÁGINA NATHALY MINIMALISTA (2026-08-16)**: `/hermosillo.html` en VPS — minimalista blanco/verde, hero "Tu contabilidad sin dolores de cabeza", CARRUSEL 5 fotos (contadora/citas SAT/declaración/importación/consultoría) con fallback degradado, chips de servicios, CTA chat IA (conectado /chat) + WhatsApp 662 349 8589. Chat flotante Naty AI integrado EN LA PÁGINA (no redirige a Telegram). **FAL_KEY VENCIDA** (401/Application not found) — regenerar en fal.ai/dashboard; script `gen_fal_photos.py` listo, carrusel apunta a `/hermosillo_assets/`.
- **AGENTE NATHALY MCP (2026-08-16)**: registry expose_as_mcp=true, skills [crm,voz,agendar_cita,sdc-company-research], composio_toolkits [telegram,whatsapp,gmail,googlecalendar,crm_library,fal]. `hermes_agents_mcp.py` expone list_agents/agent_info/agent_shell/agent_rules/agent_persona/composio_available — verificado para nathaly. Composio autenticado (happy-lantern-hare) solo IG+github ACTIVAS — conectar telegram/whatsapp/fal/gmail/calendar en Composio.
- **MODELOS LLM — ESTRATEGIA FREE (2026-08-15)**: `nvidia/nemotron-3-ultra-550b-a55b:free` (550B, $0, el más grande free) = modelo PRINCIPAL en Hermes (default, delegation, mem0, x_search) y clasificador Hermosillo. Key OpenRouter ($5) SOLO para razonamiento pesado (fallback deepseek-v4-flash-0731). Corregido: `deepseek/deepseek-v4-flash-free` NO EXISTE (400) — estaba en mem0/x_search. Fallbacks: nemotron, gemma-4-31b, gpt-oss-20b, liquid-lfm-2.5 (free) + ollama VPS. ⚠️ Modelos reasoning con max_tokens<1500 → content vacío (reasoning consume presupuesto).
- **VPS OVH — RUTA INTERMITENTE (2026-08-15)**: VPS 149.56.46.173 VIVO (7 días uptime, Docker: ollama Up 3 días + sdc-nginx). Port checker externo confirma 2222/80/443/11434 ABIERTOS. El timeout local era ruta ISP intermitente → fix: `AddressFamily inet` + `ConnectTimeout 20` en ~/.ssh/config (host ovh), usar `ssh -4`. Ollama VPS: docker container, puerto 11434, v0.32.6, modelos qwen3:4b / qwen2.5vl:3b / qwen2.5:3b / all-minilm / nomic-embed-text. Root / 80% (2.1G/2.9G, mejoró del 99%). Skill `conectividad-remota` creado. **MONITOREO (2026-08-15)**: `~/cron/vps-health.sh` (cron */10) — port checker externo + reintento ssh -4, logs en ~/cron/logs/vps-health.log.


## Aztrotech Onboarding Inteligente v2 (2026-08-07)
- **OKF actualizado**: aztrotech.pricing.json con data REAL de aztrotech.mx (Empleado Digital $999/$1999/$3999, NO antenas/instalación)
- **Servicios reales Aztrotech**: Empleado Digital (Agente IA 24/7), Automatizaciones, Plataformas Empresariales (CRM/ERP/Apps), Plataformas Especializadas (Jurídica, Inmobiliaria, Academia Interna), Diagnóstico IA Gratuito
- **Spec SDD 0004 v2**: `01_Core_Platform/09_CICD_Pipelines/Specs/SDD/0004-aztrotech-onboarding-white-label.md`
- **Archivos creados**:
  - `lead_scoring.py` — scoring determinista cold/warm/hot (max 100pts, reglas de negocio)
  - `lead_intelligence.py` — resumen empresa + objeciones + next_action (LLM + OKF)
  - `asset_generation.py` — 13 prompts evaluados Midjourney/Runway/ElevenLabs/Figma (imagen/video/mockup/audio)
  - `feedback_loop.py` — auto-mejora por reacciones (determinista + LLM síntesis)
  - `onboarding_engine.py` v2 — dual CRM (leads + intelligence) + scoring + feedback integrado
  - `lead_classifier.py` v2 — servicios reales + schema JSON estricto
  - `run_onboarding.py` — entry point (webhook server + scheduler)
  - `tests/integration/test_aztrotech_onboard.py` — 28 tests TDD, todos pasan
- **Scoring cold/warm/hot**: COLD (<40), WARM (40-69), HOT (70+). Datos básicos 30pts, intención 25pts, urgencia/autoridad 25pts, engagement 20pts.
- **Dual CRM**: leads.db + lead_intelligence (resumen, objeciones, next_action, audio_script)
- **Notificación César**: template CRM completo con score + resumen + objeciones + next_action
- **Asset prompts evaluados**: 5 imágenes (midjourney), 2 videos (runway), 2 mockups (figma), 2 audios (elevenlabs). Score 70-88/100.
- **Feedback loop**: 8 reglas deterministas (respuesta rápida/lenta, click diagnóstico, rechazo, conversión, voz, etc.)
- **White-label provision**: 1 comando crea tenant operable (registry + configs + landing + webhook)
- **Para activar**: `python3 run_onboarding.py --tenant aztrotech --port 5289` + webhook receptor

## MULTI-TENANT BOT ROUTING ✅
- **Registry creado**: tenant_router.py mantiene mapping bot → tenant → agente
- **@RyE_production_bot** → rye agent (Iván - Cheesee Assistant ecosystem)
- **@Aztro_tech_bot** → cesar agent (César - Aztrotech Hermosillo)
- **Webhook único**: multi_tenant_webhook.py recibe de ambos y enruta automáticamente
- **Para agregar cliente nuevo**: `python3 tenant_router.py --bot NewBot --tenant client_id --owner "Name" --client "Company"`
- **Memoria aislada**: cada agente tiene su propio Engram space (tenant:client_id)

## LECCIONES DE ESTA SESIÓN (2026-08-07)
- **XTTS NO TOCAR en esta laptop** (3.3GB RAM → congela con opencode+antigravity+openclaw). Usar edge-tts es-MX siempre.
- **Pipeline voz ligero (estándar)**: texto → edge-tts MP3 → ffmpeg imageio → OGG → Telegram sendVoice / wacli send --ptt. Script unificado: `01_Core_Platform/03_Agentic_Infrastructure/voice_reply.py`.
- **Multi-tenant webhook**: Requiere IP pública o ngrok. Alternativa: bot único con routing inteligente.
- **Paquetes de venta**: $999/$1999/$3999 USD configurados en OKF como tabla verificada.
- **Skills creados**: `voice-delivery/` (voz simple) + `multi-tenant-bot-factory/` (templates).
- **Gateway restart**: después de `systemctl --user restart openclaw-gateway`, esperar 10-15s antes de probar (401 temporal).
- **Verificar key**: curl `openrouter.ai/api/v1/key` con Bearer antes de asumir fallo de modelo.
- **Aztrotech NO vende antenas ni visitas técnicas**: vende Empleado Digital (Agente IA), Automatizaciones, Plataformas Empresariales. OKF actualizado con data real de aztrotech.mx.
- **ARQUITECTURA CORRECTA**: OpenClaw → agent cesar → OpenRouter LLM → Telegram bot @Aztro_tech_bot. Tools custom (scoring, intelligence, assets) via `python3 onboarding_tools.py cmd tenant args`. NO crear procesos paralelos.
- **API key válida**: sk-or-v1-934c2fa... (reemplaza sk-or-v1-28264c... expirada). Configurada como Environment= directo en systemd service (no EnvironmentFile=/tmp/sonora.env).
- **Para VPS OVH/Docker**: systemd override con Environment=OPENROUTER_API_KEY. MCP server sdc-mcp-local path: /home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/skills/mcp/servers/sdc_mcp_stdio.py
- **Bot estado**: ON, respondiendo en texto + audio (voz DaliaNeutral). 28/28 tests pasando.
- **NUEVA LECCIÓN (AUTO-SABOTAJE)**: Creé `telegram_bot_receiver.py` que compite con OpenClaw por el mismo bot token → conflicto 409, CPU 100%, laptop frozen. OpenClaw YA maneja @Aztro_tech_bot via tenant_registry.json. NO crear procesos paralelos.
- **NUEVA LECCIÓN (KEY EXPIRADA)**: La key en `.bashrc` (f78814...) expiró. La válida estaba en `~/.hermes/.env` (28264c...). Siempre verificar créditos ANTES de asumir fallo de modelo.
- **NUEVA LECCIÓN (RESTART SIN VERIFICAR)**: Matar y reiniciar procesos sin verificar si están corriendos crea más consumo CPU. ANTES: `ps aux | grep nombre` → decidir SI reiniciar.
- **NUEVA LECCIÓN (CÓDIGO SIN PLAN)**: Generé 6 módulos sin verificar si OpenClaw ya hacía esto. Seguir SDD: SPEC antes de CODE. Si OpenClaw + agentes + tools ya resuelven, mi trabajo es DOCUMENTAR, no crear alternativas.
- **ARQUITECTURA CORRECTA**: OpenClaw → agent cesar → tools (onboarding_engine, lead_scoring, etc). NO: telegram_bot_receiver → todo custom.
- **Aztrotech Bot Arch Analysis (2026-08-08)**: conversation_engine.py (RAG-first 10-step pipeline) + lead_classifier.py (hybrid rules+LLM) + identity.py (cold/warm/hot) + persistence.py (dual Postgres+Engram async). Postgres corre en localhost:5432 pero auth falla con password default. MCP servers disponibles: sdc-mcp-local (okf_query, log_task, get_insights), filesystem, github, fetch. Self-improvement engine en 01_Core_Platform/05_SelfImprovement/ con evaluator.py + autonomous_loop.py. Sessions JSONL en ~/.openclaw/agents/cesar/sessions/.
- **Gap detectado**: Cero dashboard CRM web para César. Data de conversaciones existe en Postgres pero no hay UI para ver leads, scoring, citas, reportes de audio.
- **Skill creado**: `architecture-discovery/` — patrón de 4 herramientas paralelas para mapear codebase antes de codear.

## LECCIONES 2026-08-09 (loop auto-mejora)
- **Ollama $0 en OpenClaw**: provider en `models.providers.ollama` (NO providers.custom), `api:"ollama"`, baseUrl SIN `/v1`, apiKey `"ollama-local"` para LAN. Para IP pública (VPS) → `OLLAMA_API_KEY=ollama-local` en Environment= del servicio systemd + restart (el gateway hot-reloada config, NO env).
- **Error "Auth lookup failed for provider ollama"** = baseUrl a IP pública sin credencial. Fix: OLLAMA_API_KEY env.
- **Bots rye + cesar reactivados**: gateway restarted con ollama/qwen3:4b, ambos bots de Telegram conectados (@RyE_production_bot, @Aztro_tech_bot).
- **Precios César FINALES**: setup $799; mensualidad $99 (1 agente/1M tok), $149 (2-3 agentes/3M), $249 (4+/6M); tokens extra $5/M; voz clonada +$200/+$50. Spec 0005 + deck + audios actualizados.
- **Orbe redirige a Telegram** (@Aztro_tech_bot), NO WhatsApp. Deck CTAs también.
- **wacli**: mismatching MAC → `wacli sync --store ~/.config/wacli`. NUNCA auto-enviar al número del bot (6623538272). Media grande a contacto con "old counter" = sesión cifrada desincronizada, texto sí funciona. Envíos MCP secuenciales (paralelos dan store locked).
- **Deck paquete César**: `02_Client_Projects/Aztrotech/04_Deployment/presentation/` (8 slides + 8 audios Dalia + preview/ con PNGs y PDF). Orbe: `orbe/`.
## FIX 2026-08-10 (tarde)
- **Voice service 24/7**: service `sdc-aztrotech-voice.service` fallaba con `CHDIR` tras reorganización. Fix: WORKINGDIRECTORY → path actual (`02_Client_Projects/Aztrotech/02_Source_Code`). Activo `(running)` desde 18:59.
- **Rate limiting per-tenant**: Decorador `@rate_limit(max_requests=20, window=60)` en `/api/chat`. Test OK: 20 req → 429.
- **clean_for_tts() anti-repetición**: Regex filtra símbolos (→ ↘ ⇿) + gestos verbalizados "(mano hacia abajo)", "(diagonal)" antes de edge-tts.
- **Git push BLOCKED**: GitHub secret scanning detecta key en history de remote branches. Nuestros commits locales están limpios. Requiere admin approval en: https://github.com/sonoradigitalcorp-H/Sonora-Digital-Corp/security/secret-scanning/unblock-secret/3HkcopWzX6Q84r63KsvaNeTZdhv
- **Skill actualizado**: `voice-delivery/SKILL.md` incluye patrón clean_for_tts + rate limiting

## FIX 2026-08-16 (esta sesión)
- **Hermes API server port conflict**: API_SERVER_PORT=8643 colisionaba con gateway principal (puerto 8643). Fix: cambiado a 8642 en ~/.hermes/.env + nginx proxy_pass actualizado a 8642. API server responde en 127.0.0.1:8642.
- **WhatsApp bridge crash loop deshabilitado**: WHATSAPP_ENABLED=false en .env y config.yaml. Bridge Baileys con sesión expirada causaba restart infinito del gateway (exit code 1 → systemd restart → loop).
- **Telegram bots NO conectados**: Solo api_server.enabled=true en config.yaml. Bots cesar (@Aztro_tech_bot), rye (@RyE_production_bot), nathaly (@HermosilloCont_bot) tienen tokens en .env pero telegram.enabled=false.
- **VPS OVH nginx sin config sonoradigitalcorp.com**: Docker nginx (sdc-nginx) sirve /mnt/vps-data/html con config default de Debian. DNS apunta a VPS (149.56.46.173) pero nginx no tiene virtual host para nuestro dominio. Config debe ir en /mnt/vps-data/nginx.conf (montado como /etc/nginx/conf.d/default.conf en container).
- **Website files copiados a VPS**: index.html, chat.html, paquetes.html, agentes.html en /mnt/vps-data/html/ via scp.
- **Redact.py fix para Python 3.10**: possessive quantifiers (++,*+) no soportados → reemplazados con +,* en agent/redact.py.

## PENDIENTES CRÍTICOS (2026-08-16)
1. **Deploy nginx config a VPS**: Actualizar /mnt/vps-data/nginx.conf con virtual host sonoradigitalcorp.com + proxy /api/ → 127.0.0.1:8642 (o tunnel al gateway local).
2. **Habilitar Telegram bots en Hermes**: config.yaml → telegram.enabled=true + tokens correctos por tenant.
3. **Multi-tenant webhook corriendo**: Levantar multi_tenant_webhook.py en puerto 5289 (o integrar en Hermes).
4. **Orbe + voz en web**: chat.html usa API endpoint, necesita TTS edge-tts → OGG → voice response.
5. **Whalink funcional**: wacli/whatsapp link generable y funcional.
6. **E2E tests TDD/BDD**: Gherkin scenarios para onboarding, chat, voice, multi-tenant.
7. **Eval prompts**: Benchmark de prompts de venta/agentes contra nemotron free.
