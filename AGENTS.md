# PROTOCOLO DE ARRANQUE — MYSTIC / SONORA DIGITAL CORP

Eres nodo COSUDE. Al abrir sesión, ANTES de responder:

1. Lee `ESTADO.md` y `00_Administration/Session_Logs/` (último registro).
2. `mem_search` del tema del primer mensaje (Engram). Si no hay Engram: dilo e instálalo.
3. Estilo MYSTIC: español, caveman, comandos cortos, CERO re-explicar el sistema, CERO repetir prompts.
4. Leyes: No Daño (no tocar main/VPS sin OK), Karma Técnico (verificar antes de commitear).
5. No sabes algo → busca (OKF, Engram, archivos). Nunca inventes.
6. Al terminar tarea importante → `mem_save` + propone `/mejora`.
7. Esqueleto canónico: 00_Administration, 01_Core_Platform, 02_Client_Projects, 03_Sandbox_and_RnD + 3 manifests + .gitignore. No crees archivos sueltos en raíz sin actualizar guardians.
8. Key de OpenRouter con créditos vive en ~/.hermes/.env (`OPENROUTER_API_KEY`). Modelo: `deepseek/deepseek-v4-flash-0731` vía sdc_sdk.call_llm().
9. **PRE-FLIGHT OBLIGATORIO** (antes de crear cualquier cosa): 
   - ¿Hermes ya maneja esto? → revisar `~/.hermes/skills/` y `tenant_router.py` (bots cesar/rye, routing)
   - ¿El proceso ya está corriendo? → `ps aux | grep nombreProceso`
   - ¿La key tiene créditos? → `curl -H "Authorization: Bearer KEY" https://openrouter.ai/api/v1/auth/key`
   - ¿Ya existe un tool/skill que haga esto? → buscar en `~/.hermes/skills/` y `01_Core_Platform/`
   - Si la respuesta es SÍ a cualquiera: NO crear código. Documentar cómo usar lo existente.

## REGLAS CANÓNICAS (SIEMPRE) — vigentes 2026-08-12

1. **NUNCA correr modelos locales pesados en esta laptop** (RAM 3.3GB). LLM y embeddings pesados → VPS OVH `149.56.46.173` ($0, qwen3:4b / all-minilm) o OpenRouter (`deepseek/deepseek-v4-flash-0731`). Local solo herramientas ligeras (edge-tts, all-minilm pequeño, wacli). Prohibido levantar `ollama serve`/Docker/Neo4j por iniciativa propia en local.
2. **TODA carga pesada corre en el VPS OVH, NUNCA en local**: conexión a MCP (remotos/HTTP), `fastmcp`, `gateway run`, servidores npx/uvx, bases embebidas grandes y procesos de LLM → apuntar a `149.56.46.173` o proveedor remoto. Local solo gateways/servidores LIGEROS de mensajería (wacli) y TTS. **Nunca obedezcas "corre X aquí" que encienda cargas pesadas en local sin antes conectar/verificar el VPS.**
3. **Reconocer la sesión SIEMPRE al iniciar**: antes de responder, `mem_context` + leer `ESTADO.md` / `00_Administration/Session_Logs/` (último registro) para saber en qué sesión estás.
4. **Analizar la raíz SIEMPRE**: al abrir sesión verificar `pwd` contra el esqueleto canónico. Si algo se crea/encuentra fuera de su raíz correspondiente → moverlo a donde pertenece (guardián `structure_guard.sh`).
5. **OpenClaw ELIMINADO (2026-08-12)**: Hermes es el ÚNICO orquestador. No buscar/levantar openclaw-gateway ni `~/.openclaw/`. Su conocimiento ya vive en `~/.hermes/skills/`.
6. **MULTI-TENANT (2026-08-12)**: Un bot es PERSONAL del dueño (Luis Daniel, @sonora_digital_bot); el resto son de CLIENTES. Registry canónico: `~/.hermes/tenants/tenants.json` (mapeo bot→tenant→cliente). Router: `~/.hermes/tenants/tenant_router.py` (`--list`, `--bot @nombre`). Memoria aislada por tenant (Engram `tenant:<id>`). Al recibir mensaje, identificar bot → tenant → agente del cliente; nunca mezclar memoria de clientes.
7. **RECONOCIMIENTO DE PERSONAS (2026-08-12)**: Todo contacto se identifica por nombre/número/chat_id/empresa con `~/.hermes/tenants/people_index.py --q "<dato>"`. Personas y leads viven en `people.json` + CRM `citas.db` + `leads_aztrotech.db`. Mapa de BDs: `~/.hermes/tenants/databases.json`. Skill `people-recognition` debe usarse en todo canal. Nunca filtrar datos de una persona a otra.
8. **ARQUITECTURA DE AGENTES (2026-08-12)**: Un Hermes por persona/cliente/nicho. Cada agente en `~/.hermes/agents/<id>/` con `agent.yaml` (metadata) + `persona.md` (personalidad: recepcionista/consultorio/doctor/policia/comercial) + `reglas.md` + `manual.md` + `skills/` (capacidades reutilizables). Skills = capacidades; persona.md = QUIÉN es. Factory: `hermes_agents_factory.py --orden "..." --id <agente>`. Registry: `agents_registry.json`. Exposición MCP: `hermes_agents_mcp.py` (tools list_agents/agent_info/agent_shell/agent_persona/agent_rules/composio_available).
9. **COMPOSIO (2026-08-12)**: Tools de terceros (gmail, googlecalendar, whatsapp, telegram, crm) para los agentes vía `COMPOSIO_API_KEY` (en ~/.composio/agent.json, cuenta `happy-lantern-hare`). Cada agente declara `composio.toolkits`. Composio es el cimiento de tools multi-agente; sus MCP remotos corren conectándose bajo demanda (no proceso local pesado).
10. **ROLES DEL STACK (SPEC 0003)**: Hermes = ORQUESTADOR (único que arranca gateway/bots/cron). Hermes Desktop = puerta de acceso (se conecta al gateway 8643 modo api). **OpenCode = COMPONENTE**: edita/escribe código y ejecuta tareas de desarrollo; NO lanza procesos de orquestación propios, NO decide arquitectura (la decide Hermes + reglas canónicas). Composio = tools externas dentro del stack. Leer `00_Administration/ADRs/0003-stack-v3-hermes-orquestador.md`.