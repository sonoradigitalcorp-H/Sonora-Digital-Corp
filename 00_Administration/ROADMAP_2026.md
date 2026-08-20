# ROADMAP 2026 — Automatización 24/7 Completa (Visión Maestra)

> Fuente: directiva del dueño 2026-08-17 (obs Engram #691). Investigación de expertos completada (obs #692).
> Principios: NUNCA loops infinitos · rate limit texto/voz · ciberseguridad · todo trazable · todo agentificado · Hermes orquesta todo.

---

## FASE 0 — CIMIENTOS (base ya operativa)
- [x] VPS OVH funcional (gateway :8643, worker deepseek-v4-flash-0731)
- [x] FB publica OK (post 996764866861279_122129544584775401)
- [x] IG publica OK (media 18093212990324482) — Enhanced Controls resuelto
- [x] Composio MCP operativo (workspace sonoradigitalcorp, key ck_)
- [ ] Commit pendiente: 3 modificados + session log sanitizado

## FASE 1 — BOT SOCIAL RESPONSE (respuestas automáticas) — PRÓXIMA
Objetivo: responder DMs + comentarios FB/IG automáticamente con aprobación.
- [ ] Decisión usuario: alcance (DMs / +comentarios / +menciones)
- [ ] Decisión usuario: modo borrador (aprueba vía Telegram) vs auto
- [ ] Cron Hermes VPS cada 10 min: leer DMs/comentarios nuevos
- [ ] Dedupe SQLite (no responder 2x al mismo id)
- [ ] LLM genera respuesta (tono marca + contexto negocio)
- [ ] Publicar respuesta (FACEBOOK_CREATE_COMMENT, FACEBOOK_SEND_MESSAGE, IG replies)

## FASE 2 — PIPELINE VIDEO CORTO (Kling/fal.ai + OpenCut) 
Objetivo: reels/shorts diarios con calidad publicable, sin tocar editor.
- [ ] Verificar FAL_KEY del dueño (fal.ai API)
- [ ] Probar Kling V3 Pro 5s clip ($0.84 con audio) — endpoint fal-ai/kling-video/v3/pro/text-to-video
- [ ] Estrategia costos: Hailuo 2.3 Pro ($0.49/video) para bulk, Kling Pro para hero clips
- [ ] OpenCut: instalar opencut-controller (MCP 161 tools, control headless) en VPS
- [ ] Pipeline (modelo automatizayescala): plan semanal → corte 20-35s → 9:16 face-tracking → subtítulos karaoke → overlays marca → multipublicación
- [ ] 7 formatos expertos: storytime, top5, ¿sabías qué?, historia, tutorial, versus, POV
- [ ] Prompts guiones: 5 bloques (rol/avatar/segundos/restricciones/ejemplo voz), prohibir muletillas IA
- [ ] Carruseles bulk: Canva Bulk Create + CSV IA (3 piezas/día max, alternar reel/carrusel)

## FASE 3 — ORBE 3D + ONBOARDING INTELIGENTE (página web)
Objetivo: orbe profesional branding SDC para hablar + onboarding inteligente + FAQs.
- [ ] Stack elegido: ElevenLabs Orb (React Three Fiber, agentState, audio reactivity) o custom shader
- [ ] Estados: idle / listening / thinking / speaking (WebSocket al agente)
- [ ] Voz: edge-tts (gratis) + whisper; STT streaming
- [ ] FAQ + onboarding: clasificación de lead → producto a medida del que escribe
- [ ] Branding: colores SDC, profesional
- [ ] Deploy en sonoradigitalcorp.com

## FASE 4 — DASHBOARD REPORTES 7AM / RESUMEN 6AM
Objetivo: reporte diario automático de redes + mentiras/verdades.
- [ ] Cron 7am: reporte redes (posts, engagement, seguidores, DMs pendientes) → Telegram/WhatsApp
- [ ] Cron 6am: resumen verdades/mentiras del sistema (auditoría auto)
- [ ] Integrar métricas: FB Insights, IG Insights vía Composio
- [ ] Dashboard agentic personal (todo cliente, leads, BD, Obsidian)

## FASE 5 — BOTS NATY + PERSONAL (audio, foto, video)
- [ ] Bot Naty + bot propio: enviar audio + foto + video a cada bot (canva skill, video/edit skill)
- [ ] Probar skill Canva (carruseles/diseños) + video editing
- [ ] Referencias Lovable para entrega de páginas web con IA

## FASE 6 — INGENIERÍA + TRAZABILIDAD (transversal)
- [ ] Gherkin scenarios, spec kit, spec judge, SDD, TDD, BDD, ODD
- [ ] Test unit/integration en cada pipeline
- [ ] Workflows, triggers, pipelines, cron — TODO vía Hermes + skills nativas
- [ ] ADRs por cada decisión de arquitectura
- [ ] Integrar Obsidian + BDs (todo cliente, CRM, leads)
- [ ] Seguridad: keys solo en ~/.hermes/.env, rate limit texto/voz, logs sanitizados

## AUTOMEJORA (loop diario, SIN loops infinitos)
- [ ] /mejora diario: revisar ESTADO.md + sesiones + commits + engram → proponer 1 mejora accionable
- [ ] Max 1-2 propuestas por ciclo (cortar si no avanza)

---

## REGLAS DURAS (vigentes)
1. NUNCA loops infinitos de creación.
2. Carga pesada SIEMPRE en VPS (nunca local — RAM 3.3GB).
3. NUNCA fotos stock en campañas: assets reales (deck-slide-*.png, slide_*.png sirven).
4. Publicación con aprobación humana hasta que el dueño diga auto.
5. Verificar ANTES de decidir (pre-flight obligatorio).
6. Keys nunca en logs ni repos.
