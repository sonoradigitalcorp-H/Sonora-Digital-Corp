# Tasks: Infraestructura de Tests

---

## US1 — Modularizar tests de integración

- [x] Separar test_api.py en 3 archivos
- [x] Crear test_api_status.py (test_status, sessions, search)
- [x] Crear test_api_voice.py (voice tests)
- [x] Crear test_api_stability.py (edge cases, methodology)
- [x] Verificar 330 tests pasan sin el archivo original

## US2 — Logrotate y monitoreo

- [x] Configurar logrotate (diario, 7 días, comprimido)
- [x] Truncar logs de error existentes
- [ ] Setup alerta si logs >100MB

## US3 — CI/CD

- [ ] Añadir step de logrotate check en CI
- [ ] Tests de humo post-deploy

