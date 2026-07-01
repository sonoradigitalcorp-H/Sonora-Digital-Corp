# Lecciones — SPEC-20260701-004

## Lo que funcionó bien

1. **TDD + SPEC + Score + Gherkin**: 70 tests dieron confianza para refactorizar sync.py sin romper nada. El overhead (~30 min) se pagó múltiples veces durante debugging.

2. **Capability-first**: Forzó abstracciones correctas desde el día 1. `sync.py` no sabe ni necesita saber qué proveedor ejecuta. 0 cambios al agregar TikTok/Spotify scrapers.

3. **Pydantic models first (Fase 0)**: Tener los modelos antes que cualquier lógica evitó acoplamientos incorrectos. Los modelos son la única fuente de verdad.

4. **Fallback automático**: La decisión de probar providers en orden de weight (no health-first) nos salvó durante testing — Deezer daba 403 intermitente y Apple Music respondía sin problema.

5. **Executors separados**: Tener `http.py`, `cli.py`, `browser.py` separados permitió debuggear TikTok (Playwright) sin tocar Deezer (httpx).

## Lo que no funcionó

1. **Import paths**: `planner/__init__.py` re-exporta funciones pero algunas importaciones en `decision_engine.py` usan paths absolutos (`planner.registry.get_capability`) mientras otras son relativas. Consistencia.

2. **Browser scraping fragile**: Instagram login wall no detectable hasta runtime. TikTok HTML cambia de estructura entre sesiones. Sin tests E2E, estos errores pasan silenciosos.

3. **Health check sin blocking**: Útil en teoría, pero en la práctica ningún provider ha fallado health check mientras estaba realmente down. La caché de 5 min puede dar falsos positivos.

4. **Timeout único**: El timeout de 30s en `execute_capability()` es muy corto para TikTok browser (Playwright necesita ~45s para páginas pesadas). Necesitamos timeout por provider.

## Próxima vez

1. **Timeout por provider** en `config/registry.json` en vez de valor fijo en executor
2. **E2E tests** para scrapers browser (Playwright test runner) al agregar cada nuevo provider
3. **Consistencia de imports**: o todos absolutos o todos relativos en planner/
4. **Rate limiting por provider** antes de llegar a 10 capacidades
5. **LECCION.md en español** consistente con el equipo
