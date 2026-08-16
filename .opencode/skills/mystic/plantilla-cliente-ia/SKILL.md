# plantilla-cliente-ia

Crea un cliente nuevo con web IA conversacional (texto+voz), bot para clientes,
bot para el dueño y notificaciones WhatsApp + audio. Hereda el stack SUPERPOWERED
de Hermosillo Contabilidad (probado 25/25 tests). Reutiliza, NO re-inventa.
Siempre verificar lo que existe antes de crear (ESTADO.md, Hermes, skills).

## Cuándo usarla
Cuando llega un cliente nuevo (dueño con negocio en Sonora que quiere página web
IA + bot en su WhatsApp/Telegram). Aplica si el stack ya existe y solo cambia el
tenant.

## Modelo de negocio (2 bots por cliente)
1. Bot/asis. para los CLIENTES del negocio (captura leads, agenda, responde 24/7).
2. Bot/canal para el DUEÑO (notificaciones de leads, escalaciones, dashboard).
3. Página web IA: orbe blanco-perla + chat/texto/voz + cards de servicios + carrusel.

## Pasos (orden fijo)

### 1. Diagnóstico (siempre primero)
- Leer nueva/ESTADO.md → último sesión en 00_Administration/Session_Logs/
- Verificar skills/tools existentes en ~/.hermes/skills/ y 01_Core_Platform/
- Verificar proceso corriendo: `ps aux | grep <nombreProceso>`
- Verificar key: `curl openrouter.ai/api/v1/key` antes de asumir fallo
- Confirmar VPS OVH alcanzable: `ssh ovh "docker ps"` (si no → ruta intermitente)

### 2. Tenant + persona + reglas (agente)
- Registrar en ~/.hermes/tenants/tenants.json (bot→tenant→cliente)
- Registrar en ~/.hermes/tenants/people.json (dueño = "jefa")
- Crear agente ~/.hermes/agents/<id>/{agent.yaml,persona.md,reglas.md,manual.md}
- persona.md: SUPER COMERCIAL, vende tiempo/tranquilidad/control
- reglas.md: NUNCA inventar precios, memoria nombre, RAG, derivar al dueño
- agents_registry.json: expose_as_mcp true + skills + composio_toolkits

### 3. Webhook SUPERPOWERED (copiar de hermosillo y adaptar)
- Copiar: telegram_webhook_hermosillo.py, onboarding_hermosillo.py,
  lead_classifier_hermosillo.py, security_hermosillo.py, assets_hermosillo.py,
  seeder_rag_hermosillo.py — RENOMBRAR por cliente y adaptar servicio/faq
- Endpoints: POST /webhook/<token> (Telegram) + POST /chat (web JSON) +
  GET /chat/audio?text= (MP3 Dalia)
- Seguridad: rate limit 30/h + prompt injection + sanitize
- Notificación al dueño: WhatsApp (numero) + Telegram (chat_id) + audio
- Memoria nombre: get_nombre/guardar_nombre por chat_id/sid

### 4. KB (RAG verificada)
- Carpeta kb/{servicios,sat,beneficios}/.md con DATA VERIFICADA del rubro
- Seeder: python3 seeder_rag_<cliente>.py --rebuild (embeddings VPS all-minilm)
- Store ligero JSON (knowledge_store.json) — sin qdrant/E2E pesado

### 5. Photos con FAL (fal_client.subscribe, no curl)
- 5 fotos hero del rubro + 2 visuales: "celular con asistente respondiendo" y
  "dashboard del negocio" — prompts con beneficio para el cliente
- Subir a /mnt/vps-data/html/<cliente>_assets/ en VPS

### 6. Despliegue 24/7 VPS OVH
- Copiar a /tmp/hermes/webhooks/<cliente>/
- venv + deps (pydantic/requests/edge-tts/pytz)
- Supervisor (PIDFILE + set -a + source .env ANTES de ejecutar — CRÍTICO)
- nginx VPS: /webhook + /chat + /chat/audio + página
- setWebhook Telegram + SL ven 24/7

### 7. Tests spec-driven (siempre al final)
- tests/features/<canal>_voz.feature (Gherkin) + runner Python test_*.py
- Invariantes: single-flight, anti-eco, no solape audio, injection, paquetes,
  memoria nombre, RAG. — nunca decir "done" sin 100% PASS

## Troubleshooting frecuente (patrones aprendidos)
| Síntoma | Causa | Fix |
|---------|-------|-----|
| Respuestas genéricas | env key no heredada | set -a; source .env; set +a en supervisor |
| FAL 401/405 en curl | método | usar fal_client.subscribe (no curl GET) |
| Orbe habla en loop | mic se auto-escucha | interimResults=false + stopMic() antes de send |
| Audio solapado | múltiples Audio | cancelAudio() + single-flight busy |
| VPS inalcanzable | ruta ISP intermitente | ssh -4 + AddressFamily inet + retry |

## Exit criteria
- [ ] Diagnóstico verificado (nada duplica Hermes)
- [ ] Agent persona/reglas listos (expose_as_mcp)
- [ ] Webhook SUPERPOWERED adaptado + tests 2/100
- [ ] RAG indexado (KB verificada)
- [ ] 7 fotos FAL + carrusel
- [ ] Página orbe blanco-perla + voz/texto + micrófono
- [ ] Despliegue VPS 24/7 + setWebhook E2E
- [ ] Notificación dueño (both números) probada
- [ ] /mejora + mem_save documentado