# Lecciones — SPEC-20260701-006

## Lo que funciono bien
1. El patron de mock (unittest.mock.patch) es consistente entre todos los collectors
2. Los tests de Playwright requieren mock en `playwright.sync_api.sync_playwright`, no en el modulo del collector
3. Los collectors ya manejan errores HTTP gracefulmente (404, 403, timeout)

## Lo que no funciono
1. Los tests async con @patch requieren AsyncMock — facil de olvidar
2. TikTok y Spotify tests necesitan playwright instalado en CI aunque sea para mock

## Proxima vez
1. Agregar playwright al pip install de CI ANTES de escribir tests que lo usen
2. Probar tests en entorno limpio (sin dependencias) antes de commit
