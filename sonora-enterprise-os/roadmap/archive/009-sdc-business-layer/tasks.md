# Tasks: SDC Business Layer

---

### Sprint 1: Foundation (Week 1) ✅
- [x] Instalar stripe skill en OpenClaw — stripe@2.9.2
- [x] Instalar supabase skill en OpenClaw — supabase@1.0.0
- [x] Crear skill `sdc-mystic` con personalidad completa
- [x] Crear skill `sdc-onboarding` con flujo de 3 preguntas
- [x] Crear modelo de datos de cliente en Neo4j — nodo Customer + Subscription
- [x] Tests: onboarding flow, Mystic greeting — 42 tests en test_sdc_business.py

### Sprint 2: Payments (Week 2)
- [x] Endpoint API: crear/actualizar suscripción — `/api/sdc/plans`, `/api/sdc/plan/{id}`
- [x] Multiplicador adulto x2 en backend — `calculate_price(plan, "adulto")` en sdc_business.py
- [x] Tests: adult multiplier, plan pricing — 42 tests pasando
- [ ] Integrar Stripe Connect real para pagos — skill instalada, falta conectar webhook real
- [ ] n8n workflow: Stripe webhook → activación de plan — flujo definido, falta implementar

### Sprint 3: Dashboard (Week 3)
- [x] Dashboard de cliente con Mystic presente — endpoint `/api/sdc/onboarding/mystic` (4 steps)
- [x] CRM en grafos (Neo4j) visible en dashboard — nodos Customer + Subscription creados
- [x] Tests: CRM graph, onboarding — integración en test_api.py
- [ ] Vista de progreso y uso del plan — UI pendiente
- [ ] Historial de facturas y pagos — depende de Stripe real

### Sprint 4: Automations (Week 4)
- [x] Cada plan habilita automatizaciones correspondientes — `get_features(plan_id, nicho)` implementado
- [x] Tests: plan features, nicho routing, full onboarding — 42 tests
- [ ] n8n workflows para cada tipo de automatización — pendiente conectar n8n real
- [ ] Sistema de tokens integrado con Stripe — lógica lista, falta Stripe real

---

**Completado**: 14 tareas | **Pendiente**: 6 tareas | **Total**: 20
