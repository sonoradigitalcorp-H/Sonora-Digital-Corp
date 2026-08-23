# ESTADO VIVO

## MODELO PRINCIPAL DEEPSEEK (2026-08-23) — páginas y bots
- **`deepseek/deepseek-v4-flash-0731` = PRINCIPAL** en páginas y bots; fallback `nvidia/nemotron-3-ultra-550b-a55b:free`.
- ⚠️ **deepseek es RAZONADOR**: `content` sale vacío si `max_tokens` es bajo (todo se va a `reasoning`).
  **Requerido `max_tokens>=800`** en TODO payload (antes 220 → "Hola." o null). Subido a 800 en
  vps_ai_server.py (2 payloads) y sdc_sdk.py (call_llm). Clasificador usa 1500 (correcto).
- **Bug CÁLCULO `clean_reply` corregido**: tenía `.replace("i","")` que borraba TODAS las "i"
  (Entiendo→Entendo). Se cambió a `.replace("¡","")` (quitar exclamación invertida). Sin esto las
  respuestas salían mutiladas.
- vps_ai_server.py `MODEL_CHAIN` invertido: deepseek PRIMERO, nemotron fallback.
- lead_classifier_hermosillo.py invertido: deepseek principal, nemotron fallback (clasificación precisa).
- VPS ai server probado 3 personas (tubandera/nathaly/sdc) con deepseek → respuestas naturales y precisas.

## MULTI-LANDING POR PERSONA (SDD-0013) — 2026-08-22
- **3 marcas sobre 1 base** (`/var/www/sonoradigitalcorp/index.html` reutilizada): SDC (`?p=sdc`),
  Naty contabilidad (`?p=nathaly`, SOLO contabilidad/estrategia fiscal/contabilidad inteligente),
  y **Tu Bandera A.C.** (`/tubandera.html`, marca propia rojo/azul + fotos Gemini).
- **Persona `tubandera`** añadida a `vps_ai_server.py` (SOUL server-side + intent replies router):
  recuperación de adicciones, tono cálido, NUNCA diagnostica ni da consejo médico, deriva a humano/911.
- **Router determinista por persona**: precio/cita/silencio/ubicación responden sin LLM.
- **Mic auto-stop por silencio**: cuando el analizador detecta `avg<12` por **>1200ms**, la grabación
  se detiene sola y se envía a STT (ya no solo push-to-talk). Inyectado en index.html (sdc/nathaly) y tubandera.html.
- **Assets marca Tu Bandera**: `/var/www/sonoradigitalcorp/tubandera_assets/` (logo rojo/azul, familia,
  4 fotos Gemini 24/7). Integradas al carrusel (railImgs) de tubandera.
- **Spec**: `01_Core_Platform/09_CICD_Pipelines/Specs/SDD/0013-multi-landing-personas.md` (Gherkin).
- **Tests**: `03_Sandbox_and_RnD/tests/integration/test_sdd0013_landing.py` — **7/7 PASS** en VPS
  (3 personas LLM/router, TTS, STT, páginas HTTP, assets).

## REDISEÑO WEB CHAT + VOZ PRO MAX (SDD-0012) — 2026-08-22/23
- **Chat + voz IA en sonoradigitalcorp.com** rediseñado por completo (`/var/www/sonoradigitalcorp/index.html`).
  UI Pro Max: Three.js orbe 3D reactivo al audio (IcosahedronGeometry + shader fresnel + 520 partículas GPU),
  glassmorphism (backdrop-filter blur 24px), chat burbujas glass, mic push-to-talk, altavoz con botón STOP.
  CERO dashboard, CERO exclamaciones. Personas `?p=sdc` / `?p=nathaly` (rebrandea título, colores, hero, WA, voz).
- **Catálogo de asistentes por nicho** (8): Boutique, Consultorio, Restaurante, Taller, Abogados, Spa, Contabilidad, Gym —
  cada card con beneficios + AHORROS en $/mes + botón "Ver en acción" que lanza demo al chat. Sección "Muestras de valor" (rail Netflix).
- **Agenda visible #agendaBtn**: modal con 10 días hábiles + 8 horas; confirma → POST `/api/v1/citas` → guarda en
  SQLite `/opt/hermes/citas_db/citas_{persona}.db` + genera TTS confirmación + **wacli send voice al WhatsApp del usuario**.
  Flujo E2E verificado en navegador (cita "Cliente E2E" 2026-08-24 11:00 guardada + confirmación por WhatsApp).
- **Comando de silencio** (`SILENCE_RE`): si el usuario escribe "calla/silencio/basta/no hables/quita la voz", detiene el TTS.
- **Fix mic**: umbral blob 1200→300B + manejo de errores STT + aviso si navegador sin MediaRecorder. Sin `alert()` (feedback inline).

## STACK VOZ EN VPS OVH (149.56.46.173) — SDD-0012
- **`/opt/hermes/voice/stt_server.py`** :5292 (`sdc-stt.service`, Restart=always). faster-whisper **small int8**,
  beam_size=3, initial_prompt es-MX, lipsum strip de exclamaciones. ~2.6s/4s audio.
- **`/opt/hermes/voice/tts_server.py`** :5293 (`sdc-tts.service`). edge-tts (kokoro onnx si existiera en /opt/hermes/kokoro).
  `clean_for_tts` sin exclamaciones/emojis. ~1.0s, audio/mpeg, X-TTS-Engine.
- **`/opt/hermes/vps_ai_server.py`** :8643 (`vps-ai-server.service`) REWRITE v2:
  - `/api/v1/chat/completions` (person sdc|nathaly, SOUL server-side, chain deepseek-0731→nemotron-free, fallback offline con beneficios)
  - `/api/stt` y `/api/tts` = PROXY → :5292/:5293
  - `/api/v1/citas` = agenda + TTS + wacli send voice (WACLI_BIN env)
  - `/health` agregado (stt+tts+llm)
  - `clean_reply` (quita `!¡`, colapsa puntos) + `soft_replace_tech` (defensa en profundidad anti-palabras técnicas)
- **wacli 0.12.0** binario Go copiado al VPS (`/home/mystic/.local/bin/wacli`, AUTHENTICATED=true JID 5216623538272),
  envía voz OK. `npm i wacli` NO existe (es binario propietario, no npm).
- **nginx**: location `/api/` → 8643; location `= /health` → 8643/health. Índice nuevo desplegado, backups `.bak-0012`.

## SPECS Y TESTS SDD-0012
- **Spec**: `01_Core_Platform/09_CICD_Pipelines/Specs/SDD/0012-web-chat-voice-redesign.md`
- **Eval prompts**: `prompt_registry/eval_prompts.yaml` + `prompt_registry/run_eval.py` (juez nemotron-free, reglas duras sin exclamaciones/tecnicismos)
- **SOUL** canónico: `01_Core_Platform/01_Architecture/SOUL.md` (versión de voz, cero exclamaciones, prohibidas palabras técnicas, vendemos beneficios)
- **Tests**: `03_Sandbox_and_RnD/tests/integration/test_sdd0012_web_chat.py` — **22/22 PASS** (soul cleaning, UI copy sin malas palabras, catálogo, agenda, silencio, endpoints)

## SOUL PROMPTS REFORZADOS (objeciones + SIEMPRE cita)
- Los system prompts de `vps_ai_server.py` ahora manejan objeciones (caro→más barato que recepcionista; miedo tecnología→no tocas nada;
  no tiempo→eso te devuelve; es para grandes→es tu tamaño ideal) y SIEMPRE cierran con 2 horarios concretos de esta semana,
  NUNCA repiten el mismo escenario, y atienden comando de silencio.
- Copy vende AHORROS ($/mes), tiempo (24/7 sin sueldo), cero multas. Nunca "IA/bot/modelo/token".

## AZTROTECH BAJADO (2026-08-20)
- **Aztrotech FUERA de servicio**: solo quedan sonoradigitalcorp.com + Nathaly Hermosillo.
- Proceso `wacli_stdio.py` matado (0 procesos aztrotech). Crons de Aztrotech (ventas-cesar + Aztrotech_Citas x3) eliminados, backup en /tmp/crontab.bak-aztro-20260820.
- Token `TELEGRAM_AZTROTECH_TOKEN` comentado en ~/.hermes/.env (backup .env.bak-aztro-20260820).
- Tenant `aztrotech` eliminado de tenants.json; agente `cesar` eliminado de agents_registry.json; dir movido a ~/.hermes/agents/_archived/cesar_20260820.
- tenant_router.py sin refs aztrotech (0). Skills cesar-* (8) archivados en ~/.hermes/skills/clients/_archived_aztro_20260820/. Skill `aztrotech-citas` CONSERVADO (lo usan nathaly + consultorio-sonora). Skill `ventas-cesar` archivado en .opencode/skills/mystic/_archived_ventas-cesar_20260820.
- Proyecto movido: `02_Client_Projects/Aztrotech` → `_archived/Aztrotech_20260820/`.
- Pendiente: VPS OVH sigue caído (página sonoradigitalcorp.com down desde 2026-08-19 16:20) — requiere panel OVH zona CA.

 (se actualiza con /mejora — leer SIEMPRE al arrancar)

- Producción: VPS 187.124.85.191, usuarios Nathaly/Marco/TripleR activos, CI/CD despliega desde main.
- **RAMA DE PRODUCCIÓN = `next`** (2026-08-20): GitHub `sonoradigitalcorp-H/Sonora-Digital-Corp`, 61 commits, secretos limpiados con filter-repo, sincronizada (5b86049d). `main` = MONOREPO LEGACY CONGELADO (historia NO relacionada, 583 vulns heredadas de apps/clients/products/tenants que en next viven en _archived/ o rutas canónicas) — NO se toca ni se mergea; documentado como histórico. No hay PR posible next→main (historias no relacionadas).
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
- **VPS OVH REPROVISIONADO Y VIVO (2026-08-21)**: SO limpio reinstalado en VPS `149.56.46.173`. SSH con llave `id_ed25519_sdc` activo sin contraseña. Firewall UFW activo (puertos 22, 80, 443, 11434, 5291 abiertos). Docker + Ollama activo en puerto 11434 con modelo `all-minilm` (verificado 200 OK vía curl). Entorno `/opt/hermes/venv` listo con dependencias (pydantic/requests/edge-tts/pytz).
- **CLOUDFLARE TUNNEL MIGRADO AL VPS + STACK WEB RÁPIDO (2026-08-21)**: Tunnel `sonoradigitalcorp` migrado de la LAPTOP al VPS — web ya NO depende de la PC. cloudflared instalado en VPS (`/etc/cloudflared/config.yml`, credentials `a8f01806`), servicio systemd `cloudflared-tunnel.service` activo+enabled. Tunnel LOCAL apagado/deshabilitado. `vps_ai_server.py` en `/opt/hermes` (:8643, `vps-ai-server.service`): PRIMARY `deepseek/deepseek-v4-flash-0731` (rápido, pagado), timeout 25s, retry automático a `nvidia/nemotron-3-ultra-550b-a55b:free` si falla. Frontend (`index.html`, `chat.html` en `/var/www/sonoradigitalcorp/`) apunta a `MODEL=deepseek/deepseek-v4-flash-0731`. Latencia web-medida 1.9–2.6s HTTP 200 modelo real. Key OpenRouter de $5 = `sk-or-v1-10b4...49f` (`.env`, `limit_remaining $2.73`); key muerta `sk-or-v1-934c2fa008...` eliminada del `.bashrc` (401 User not found).
- **LANDINGS CHAT TEXTO+VOZ + WEBHOOK NATHALY EN VPS (2026-08-21)**: Quité el orbe-que-habla (Web Speech API Chrome-only) de index.html, chat.html y hermosillo.html → chat limpio texto + mic (MediaRecorder→`/api/stt`) + altavoz (`/api/tts`). `vps_ai_server.py` ahora incluye `/api/stt` (faster-whisper "base" int8 CPU es-MX, instalado en venv, ~4.3s para 6s audio, $0 privado) + personas `sdc`/`nathaly` en system prompt + MODEL_CHAIN deepseek-0731→flash-latest→nemotron. **Webhook Nathaly DESPLEGADO**: `hermosillo-webhook.service` (:5291) en VPS, código en `/opt/hermes/hermosillo/` (+ sdc_sdk, telemetry, lead_scoring, tenant_router, kb/, assets/), DB `/opt/hermes/hermosillo/db/leads_hermosillo_cont.db`. Telegram getWebhookInfo pending=0 sin error (502 resuelto). Tests E2E: web 200, chats SDC/Nathaly responden, STT transcribe, onboarding inteligente (scoring/RAG/voz/seguridad) ya activo. ⚠️ meta-webhook (:8080) PENDIENTE — depende de aprobación WABA Meta.
- **GATEWAY HERMES EN VPS (2026-08-22)**: `hermes-gateway.service` (systemd, active) en VPS `127.0.0.1:8642` (API HTTP 200 /health). Código en `/home/mystic/.hermes/hermes-agent/` (rsync del paquete + venv recreado con Python 3.12 + `pip install -e .`). Config VPS adaptada: telegram DESHABILITADO (elimina conflicto con webhook :5291 que polla el bot Nathaly; api_server es lo crítico). ⚠️ meta-webhook :8080 AÚN PENDIENTE: la ruta `/api/v1/meta/webhook` NO existe en Hermes 0.20.4 (el wa_webhook.py era del Hermes viejo) — requiere re-integración + aprobación WABA Meta.
- **WACLI VPS AUTENTICADO + KEEPALIVE 24/7 (2026-08-22)**: wacli instalado en VPS (`/home/mystic/wacli`, store `/home/mystic/.wacli`), autenticado por phone-code pairing (el store de la laptop NO es portable — AUTHENTICATED=false hasta re-pairing). `wacli-auth.service` (one-shot, se detiene al completar) + `wacli-keepalive.service` (`sync --follow`, `Restart=always`) mantiene la sesión WhatsApp viva y refrescada. Envío WhatsApp desde VPS OK (id 3EB0D950734B65CC571557, sin errores MAC/counter). ⚠️ `wacli doctor` da `locked_by_other_process` mientras el keepalive corre (NORMAL). Los 6 servicios VPS (hermes-gateway, vps-ai-server, hermosillo-webhook, cloudflared-tunnel, nginx, ollama) tienen `Restart=always` → siempre activos.
- **AGENTES HÍBRIDOS NEUTROS (2026-08-22)**: 3 agentes neutros/adaptables creados de forma determinista en `~/.hermes/agents/` y registrados en agents_registry.json: `asistente-hibrido`, `soporte-adaptado`, `comercial-flexible`. Nicho `hibrido`, modelo `nvidia/nemotron-3-ultra-550b-a55b:free`, persona adaptable (`_template/personas/hibrida.md`), skills neutras (sdc-onboarding, sdc-company-research, sdc-voice-clean, people-recognition, registrar_lead), MCP expuesto True. Se adaptan a cualquier negocio/dominio. Gateway Hermes duplicado de laptop ELIMINADO (el VPS lo corre; puerto 8642 local liberado).

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
- **MCP Composio ACTIVADO**: config.yaml → composio.enabled=true + key ck_XXXX_REDACTED_XXXX. Gateway reiniciado. Tools MCP: SEARCH, MANAGE_CONNECTIONS, WAIT, GET_SCHEMAS disponibles.
- **Meta Webhook VPS 24/7**: `wa_webhook.py` deployado en VPS :8080 → nginx `/webhook/meta` → sonoradigitalcorp.com/webhook/meta (HTTPS, verificación OK). Service `meta-webhook.service` (systemd, VPS).
- **Conexiones Composio ACTIVAS**: Facebook ✅, Instagram ✅, WhatsApp ✅, YouTube ✅ (via MCP + OAuth). LinkedIn pendiente.
- **WhatsApp Webhook suscrito**: WABA `1158874942978786` + verify_token `d49a07131999c48d4be19c7dd3f8f28d` + callback `https://sonoradigitalcorp.com/webhook/meta`. Intentado via Composio SDK (requiere toolkit_version + dangerously_skip_version_check).
- **Webhooks manuales configurados**: Instagram (messages, messaging_postbacks, message_reactions), Page (messages, messaging_postbacks, feed), Messenger (messages, messaging_postbacks) — Callback URL + Verify Token idénticos.
- **Hermes 24/7 VPS LEVANTADO**: gateway :8643, dashboard :9120, meta-webhook :8080, hermosillo :5291. `restart.sh` actualizado con paths correctos.
- **Unificación completada**: `Hermes Millonario` archivado en `_archived/`. `~/.hermes/` = single source of truth. Local meta-webhook apagado (redundante). VPS = único público 24/7.
- **Grafo ecosistema actualizado**: `00_Administration/Grafo_Ecosistema_SDC.html` con estado 2026-08-16 (nemotron free principal, nathaly agent, hermosillo client, API 8642, MUAPI, skills actuales).

## PENDIENTES CRÍTICOS (2026-08-16)
1. **WABA approval**: Esperar aprobación Meta (Review in Progress → Approved) para suscribir `message_deliveries`, `message_reads`, `messaging_postbacks`, `message_echoes` en WhatsApp.
2. **Telegram bots en Hermes**: config.yaml → telegram.enabled=true + tokens por tenant (cesar/rye/nathaly/sonora).
3. **LinkedIn en Composio**: Conectar OAuth via MCP (`composio link linkedin`).
4. **FAL_KEY regenerar**: vencida 401 → fal.ai/dashboard para campañas IG + assets Hermosillo.
5. **Orbe + voz en web**: chat.html → TTS edge-tts → OGG → voice response.
6. **Whalink funcional**: wacli/whatsapp link generable y funcional.
7. **E2E tests TDD/BDD**: Gherkin scenarios para onboarding, chat, voice, multi-tenant.
8. **Eval prompts**: Benchmark prompts venta/agentes vs nemotron free.
9. **Apagar Meta Business Agent**: En WhatsApp Business → Tools → IA Agent → "Paused for new chats but learning".

## SESIÓN 2026-08-20 (hoy)
- **Orbe IA web con voz** implementado en 3 páginas:
  - `index.html` (landing principal): orb + chat + mic (Web Speech API) + TTS edge-tts
  - `chat.html` (widget embebible): mismo patrón, mic + send + voice response
  - `hermosillo/index.html` (panel flotante sobre orbe 3D): chat panel + mic + TTS
- **CORS fix**: `api_server.extra.cors_origins: "*"` en `~/.hermes/config.yaml` → reinicio `hermes-gateway.service`. Browser Origin requests ahora 200 OK.
- **WhatsApp button repositioned**: right:112px (era right:24px) para no interceptar clicks del orb (right:24px, z-index 9998 vs 9999).
- **nginx timeout**: proxy_read_timeout 60s → 120s en `/api/v1/` para evitar 504 en LLM responses.
- **VPS OVH status**: Panel "Activo" pero TODOS puertos cerrados (22, 80, 443, 11434, 8080, 5291). Reboot no arregló. Requiere VNC console → rescue mode → fix systemd/docker/network.
- **Local Ollama STOPPED**: `systemctl --user stop/disable ollama.service` — libera ~1.5GB RAM en laptop 3.3GB. VPS OVH (149.56.46.173) = único lugar para embeddings/LLM.
- **Audio resumen enviado a WhatsApp**: 2 min voz DaliaNeural via edge-tts → ffmpeg → wacli send voice (id 3EB00B9F422185CC13D948).

## PENDIENTES ACTUALIZADOS (2026-08-20)
1. **VPS OVH recovery**: VNC console → diagnose → rescue mode si no responde. Backup 2026-08-20 03:26 disponible.
2. **FAL_KEY regenerar**: vencida 401 → fal.ai/dashboard.
3. **LinkedIn en Composio**: `composio link linkedin`.
4. **Telegram bots en Hermes**: telegram.enabled=true + tokens por tenant.
5. **WABA approval**: esperar Meta.
6. **Whalink funcional**: wacli link generable.
7. **E2E tests TDD/BDD**: Gherkin scenarios.
8. **Eval prompts**: Benchmark vs nemotron free.
9. **Apagar Meta Business Agent**: WhatsApp Business → IA Agent → Paused.
