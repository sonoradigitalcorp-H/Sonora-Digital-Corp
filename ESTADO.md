# ESTADO VIVO (se actualiza con /mejora — leer SIEMPRE al arrancar)

- Producción: VPS 187.124.85.191, usuarios Nathaly/Marco/TripleR activos, CI/CD despliega desde main.
- Repo: rama `master` local; GitHub remoto `sonoradigitalcorp-H/Sonora-Digital-Corp`. Rama `next` pendiente de crear/pushear (main intocada).
- Modelo: `deepseek/deepseek-v4-flash-0731` (OpenRouter). Key con créditos: sk-or-v1-282...732 ($10/mes) en /tmp/sonora.env + ~/.hermes/.env. La key anterior (327...cb7) quedó sin saldo.
- Engram: v1.19.0, plugin opencode instalado (memoria persistente entre sesiones). Memoria #474 guardada.
- OpenCode COSUDE: AGENTS.md + ESTADO.md + /idea /validar /mejora /contexto + @orquestador @clientes @redes @voz + skill estilo-mystic. Reiniciar opencode para cargar.
- Hermes Agent Factory: Orquestador/hermes_agent_factory.py + hermes_supervisor.py. Auto-crea agentes OpenClaw desde orden natural. Agente demo `cesar` (Aztrotech) enlazado a telegram, operativo.
- Gateway OpenClaw: openclaw-gateway.service carga OPENROUTER_API_KEY via /tmp/sonora.env. Modelo de los 4 agentes = openrouter/deepseek/deepseek-v4-flash-0731.
- **Modelo ID correcto**: `openrouter/deepseek/deepseek-v4-flash-0731`. NO `opencode/deepseek-v4-flash` (billing opencode.ai, 401) ni `openrouter/deepseek/deepseek-v4-flash` sin sufijo (Unknown model).
- Clientes a activar: Aztrotech, ABE Music Group. RYE (Iván Guerrero) bot ActivoGo/RyE_production_bot, Aztroc_Assistant (cesar).
- Voice Clone César: Assets listos → Audio WAV (108s), 9 fotos → pipeline voice_cloner.py + image_cloner.py esperando XTTS/FAL para entrenar modelos. Sin XTTS instalado, usar TTS genérico (es-MX-JorgeNeural) mientras.
- **Voz SIMPLE funcionando (sin XTTS)**: script `01_Core_Platform/03_Agentic_Infrastructure/voice_reply.py` hace texto→edge-tts→OGG→Telegram sendVoice en 1 comando. Probado OK en @Aztro_tech_bot y @RyE_production_bot. Voz real de César enviada al chat para comparar. Skill voice-delivery creado.
- Landing Page Onboarding: Generada en 04_Deployment/onboarding/index.html (Three.js + branding Aztrotech). Botón WhatsApp + Web.
- Pipeline Auto-Deploy: auto_deploy.py + scripts media ready. Ejecutar cuando se instale XTTS o se configures FAL_KEY para voice/image cloning.
- Redes: playwright dry-run con fotos pendiente.
- Pendiente crítico: Nginx → /panel/login, login devuelva 200.
- Guardianes: pre-commit + structure_guard.sh (esqueleto canónico).
- **⚠️ PC 3.3GB RAM — REGLA DE ORO**: Cero procesos pesados en local. LLM (qwen3:4b) y embeddings → VPS OVH (149.56.46.173). Si la PC se congela: `free -m` (RAM<400MB = crítico), kill duplicados openclaw (`ss -tlnp | grep 18789`), swap 2.3GB = swap-thrash. **GUARDIA AUTOMÁTICO**: `01_Core_Platform/04_Automations_and_Workflows/memory-guard.sh` (cron */5) mata duplicados + MCP accesorios. NO crear procesos pesados nuevos en local.
- **Embeddings DUAL (2026-08-10)**: Ollama LOCAL activo (systemd `ollama.service`, enable --now, 127.0.0.1:11434) con `tinyllama:1.1b` + `nomic-embed-text` (768-dim). VPS OVH `149.56.46.173:11434` (docker) con `all-minilm` (384-dim) + qwen3:4b + qwen2.5. Script embedding usa `OLLAMA_ENDPOINT` (de ~/.hermes/.env = VPS). Qdrant local 6333 con colecciones por tenant: kb_rye, kb_aztrotech, hermes, tenant_aztrotech (384 dims, Cosine). ⚠️ `all-minilm` local NO instalado aún (45.9 MB) — bajar si se quiere embeddings local sin depender del VPS.
- **MCP server movido (2026-08-10)**: `skills/mcp/servers/sdc_mcp_stdio.py` (deriva en raíz) → `01_Core_Platform/03_Agentic_Infrastructure/MCP_Servers/sdc_mcp_stdio/`. Test integration → `03_Sandbox_and_RnD/tests/integration/`. Launcher Antigravity → `~/.local/share/applications/`. `citas.db` vacío borrado. Structure guard VERDE.
- **INFRAESTRUCTURA SYSTEMD 24/7 VIVA (2026-08-10)**: Servicios `openclaw-gateway.service` (PID 61185), `multi-tenant-bot.service` (PID 61186) y `wacli-gateway.service` (PID 61187) configurados y activos bajo supervisión systemd user con Linger habilitado (`mystic`). Entrypoint `run_multi_tenant.py` creado y commiteado. Bots operando 24/7 sin intervención manual.


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