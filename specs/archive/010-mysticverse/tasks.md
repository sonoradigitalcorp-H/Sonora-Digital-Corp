# Tasks: Mysticverse

---

### Sprint 1: Foundation (Week 1) ✅
- [x] Instalar fal-ai, printful, supabase skills — fal-ai@0.1.0 instalado
- [x] Crear skill `sdc-digital-twin` — pipeline foto → clon → bot
- [x] Crear skill `sdc-content-adult` — generación contenido NSFW
- [x] Crear skill `sdc-kyc` — verificación edad + identidad + consentimiento
- [x] Configurar perfil "adulto" en routing del orquestador — NICHO_PROFILES["adulto"] con multiplier x2
- [x] Tests: clon creation, adult routing — 29 tests en test_mysticverse.py

### Sprint 2: Bot + Sales (Week 2)
- [x] Pipeline de ventas: lógica de pricing implementada
- [x] Multiplicador x2 aplicado en checkout
- [x] Tests: adult multiplier, pricing
- [ ] Bot Telegram real para creadora con su personalidad — pipeline listo, falta deploy
- [ ] Stripe Connect para payout a creadoras — skill instalada, falta webhook real

### Sprint 3: Content + KYC (Week 3)
- [x] KYC pipeline: edad + identidad + consentimiento — 3 fases implementadas
- [x] Tests: KYC workflow, age verification
- [ ] Generación automática de fotos diarias (fal.ai) — skill instalada, falta conectar
- [ ] Generación automática de videos cortos — skill instalada, falta conectar
- [ ] Programación de contenido con n8n — flujo definido, falta implementar

### Sprint 4: Gamification (Week 4) ✅
- [x] Motor de gamificación (XP, niveles, badges) — src/core/gamification.py completo
- [x] Leaderboard de fans para creadora — endpoint `/api/mysticverse/gamification/leaderboard`
- [x] Contenido exclusivo desbloqueable por nivel — LEVELS con benefits por nivel
- [x] Tests: gamification XP, level up, badge award — 29 tests

---

**Completado**: 15 tareas | **Pendiente**: 5 tareas | **Total**: 20
