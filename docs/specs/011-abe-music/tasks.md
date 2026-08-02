# Tasks: ABE MUSIC

---

### Sprint 1: CRM Foundation (Week 1) ✅
- [x] Modelo de datos: Artist, Release en Neo4j — nodos + constraints + índices
- [x] API endpoints para CRUD de artistas — `/api/abe/artists/*`
- [x] Dashboard CEO con KPIs desde Neo4j — `src/core/abe_music.py` KPIDashboard
- [x] Tests: CRM graph, CEO dashboard — 21 tests en test_abe_music.py

### Sprint 2: Artist Portal (Week 2)
- [x] Herramientas AI: lógica de revenue split implementada — ROYALTY_SPLIT completo
- [x] Dashboard personal del artista — endpoint `/api/abe/dashboard/artist/{id}`
- [x] Tests: music generation structure, artist KPI
- [ ] Portal de artista con login — UI pendiente
- [ ] Conexión real con fal.ai para generación música/video — skill instalada, falta integrar

### Sprint 3: Distribution (Week 3)
- [x] Stripe Connect para payout a artistas — lógica de revenue split lista
- [x] Tests: distribution pipeline, royalty tracking — 21 tests
- [ ] n8n workflow: upload → distribución → royalties
- [ ] Notificaciones automáticas (lanzamientos, ventas) — vía Hermes pendiente

### Sprint 4: Legal + Scale (Week 4)
- [ ] Contratos AI generados automáticamente
- [ ] Reportes fiscales mensuales
- [ ] KYC para nuevos talentos — skill sdc-kyc existe, falta conectar al flujo ABE
- [ ] Tests: contract generation, KYC workflow

---

**Completado**: 8 tareas | **Pendiente**: 8 tareas | **Total**: 16
