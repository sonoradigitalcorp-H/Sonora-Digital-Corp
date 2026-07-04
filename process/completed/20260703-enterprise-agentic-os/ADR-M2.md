# ADR — Nginx Gateway: All internal services bound to 127.0.0.1

| Campo | Valor |
|-------|-------|
| **ID** | ADR-M2-001 |
| **Fecha** | 2026-07-03 |
| **Estado** | aceptado |

## Contexto

4 servicios estaban expuestos en 0.0.0.0 (puertos :5180, :8111, :8080, :8931) además de :3001 y :4000 de Mystika, accesibles desde cualquier IP. Política P3 exige que ningún servicio exponga 0.0.0.0 sin nginx proxy.

## Decisión

Mover todos los servicios a 127.0.0.1 y usar nginx como único entry point público (puertos 80/443). SSL certs de Let's Encrypt con permisos 755 en `/etc/letsencrypt/live/`.

## Servicios afectados

| Puerto | Servicio | Fix |
|--------|----------|-----|
| 5180 | ABE Service | `--host 0.0.0.0` → `127.0.0.1` |
| 8111 | ABE API (abe-api.service) | `--host 0.0.0.0` → `127.0.0.1` |
| 8080 | Evolucion Dashboard | `--bind 127.0.0.1` |
| 8931 | Playwright MCP Docker | Container removed (not in compose) |
| 3001 | Mystika Web | `next start -H 127.0.0.1` |
| 4000 | Mystika API | `app.listen(PORT, '127.0.0.1')` |

## Consecuencias

- Positivas: Seguridad mejorada, superficie de ataque reducida, compliance con P3
- Negativas: Servicios externos ya no pueden acceder directamente, deben pasar por nginx
