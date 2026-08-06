# ESTADO VIVO (se actualiza con /mejora — leer SIEMPRE al arrancar)

- Producción: VPS 187.124.85.191, usuarios Nathaly/Marco/TripleR activos, CI/CD despliega desde main.
- Repo: rama `master` local; GitHub remoto `sonoradigitalcorp-H/Sonora-Digital-Corp`. Rama `next` pendiente de crear/pushear (main intocada).
- Modelo: `deepseek/deepseek-v4-flash-0731` (OpenRouter). Key con créditos: en ~/.hermes/.env (alias sk-or-v1-327...cb7).
- Engram: v1.19.0, plugin opencode instalado (memoria persistente entre sesiones). Memoria #474 guardada.
- OpenCode COSUDE: AGENTS.md + ESTADO.md + /idea /validar /mejora /contexto + @orquestador @clientes @redes @voz + skill estilo-mystic. Reiniciar opencode para cargar.
- Hermes Agent Factory: Orquestador/hermes_agent_factory.py + hermes_supervisor.py. Auto-crea agentes OpenClaw desde orden natural. Agente demo `cesar` (Aztrotech) enlazado a telegram, operativo.
- Gateway OpenClaw: openclaw-gateway.service ahora carga OPENROUTER_API_KEY via /tmp/sonora.env (se creó; antes no existía y agentes morían).
- Clientes a activar: Aztrotech, ABE Music Group. RYE (Iván Guerrero) bot ActivoGo/RyE_production_bot, Aztroc_Assistant (cesar).
- Voice Clone César: Assets listos → Audio WAV (108s), 9 fotos → pipeline voice_cloner.py + image_cloner.py esperando XTTS/FAL para entrenar modelos. Sin XTTS instalado, usar TTS genérico (es-MX-JorgeNeural) mientras.
- Landing Page Onboarding: Generada en 04_Deployment/onboarding/index.html (Three.js + branding Aztrotech). Botón WhatsApp + Web.
- Pipeline Auto-Deploy: auto_deploy.py + scripts media ready. Ejecutar cuando se instale XTTS o se configures FAL_KEY para voice/image cloning.
- Redes: playwright dry-run con fotos pendiente.
- Pendiente crítico: Nginx → /panel/login, login devuelva 200.
- Guardianes: pre-commit + structure_guard.sh (esqueleto canónico).

## MULTI-TENANT BOT ROUTING ✅
- **Registry creado**: tenant_router.py mantiene mapping bot → tenant → agente
- **@RyE_production_bot** → rye agent (Iván - Cheesee Assistant ecosystem)
- **@Aztro_tech_bot** → cesar agent (César - Aztrotech Hermosillo)
- **Webhook único**: multi_tenant_webhook.py recibe de ambos y enruta automáticamente
- **Para agregar cliente nuevo**: `python3 tenant_router.py --bot NewBot --tenant client_id --owner "Name" --client "Company"`
- **Memoria aislada**: cada agente tiene su propio Engram space (tenant:client_id)