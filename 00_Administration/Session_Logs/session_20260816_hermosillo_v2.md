# Sesión 2026-08-16 — Hermosillo SUPERPOWERED v2 (RAG, paquetes, memoria, visual, skill)

## Contexto
Continuación del bot de Nathaly (@HermosilloCont_bot). Usuario pidió: superpoderes
nivel senior (onboarding proactivo, voz, fotos, paquetes, RAG SAT, memoria de nombre),
24/7 en VPS OVH, correo, página orbe blanco-perla con micrófono, 2 bots por cliente,
skill de plantilla anti-repetición, commit + /mejora.

## Logrado
### Arquitectura (productiva 24/7 VPS OVH)
- Webhook SUPERPOWERED: POST /webhook (Telegram) + POST /chat (web JSON con sid) + GET /chat/audio (MP3 Dalia)
- Supervisor persistente `/tmp/hermes/supervisor_hermosillo.sh` (PIDFILE + `set -a` env FIX)
- nginx VPS: /webhook → 5291, /chat → 5291/chat, /chat/audio, hermosillo.html + hermosillo_assets/
- Telegram setWebhook → https://sonoradigitalcorp.com/webhook/<token>

### RAG (data verificada)
- kb/{sat,servicios,beneficios}/*.md ground truth SAT + oferta + enganche psicológico
- seeder_rag_hermosillo.py → knowledge_store.json (17 chunks, embeddings VPS all-minilm 149.56.46.173)
- Respuesta SAT precisa verificada en prod ("constancia de situación fiscal")

### Conversación / venta
- Memoria de nombre por chat (get_nombre/guardar_nombre) → saluda por nombre
- 3 paquetes determinista (Orden/Control/Crecimiento) sin precios → WhatsApp con Nathaly
- Visual de beneficio: vision_celular_asistente + vision_dashboard (FAL flux/dev)
- persona.md / reglas.md v2: super comercial (vende tiempo/tranquilidad/control)

### Web (blanco-perla, no negro)
- Three.js orbe LATERAL (no tapa carrusel), cards 6 servicios, carrusel 5 fotos,
  micrófono Web Speech (interimResults=false + stopMic antes de send → SIN LOOP),
  audio de respuesta Dalia MP3, correo cp.nathalyhermosillo@gmail.com,
  filtro anti-eco + single-flight (busy)

### Seguridad / tests
- rate limit 30/h, prompt injection INJECTION_RE, sanitize
- tests spec-driven BDD 25/25 + RAG + paquetes (test_chat_voz_regresion.py + features/)

### Anti-repetición
- **Skill `plantilla-cliente-ia`** (.opencode/skills/mystic/) — plantilla completa: tenant,
  agente, webhook, RAG, fotos FAL, despliegue VPS, tests. TROUBLESHOOTING patrones.

## Fallos corregidos
1. Supervisor sin `set -a` → python no hereda env (OPENROUTER_API_KEY) → fallback genérico
2. notify_jefa typo `siempre_siempre` → `ambos_siempre`
3. Mic en loop: re-arrancaba onend + interim → auto-captura del audio del bot
4. Audios solapados → cancelAudio() + busy
5. FAL por curl fallaba (401/405) → fal_client.subscribe funciona
6. VPS sin ffmpeg → /chat/audio devuelve MP3 (edge-tts nativo)
7. INSERT conversaciones sin tenant (NOT NULL) → agregar tenant

## Commits
- 88addf2f feat: Hermosillo SUPERPOWERED v2 (31 files, +9468)

## Pendientes
- F3 dashboard CRM

## Próxima mejora
- Usar skill plantilla-cliente-mult para nuevos clientes (Índice, consultas, economía)