# Sonora Affiliates — Portal de Afiliados y Referidos

## ¿Qué hace?
Programa de referidos completo con tracking de comisiones en tokens y MXN,
links wa.me personalizados, leaderboard y pagos.

## API
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/affiliates` | Crear afiliado |
| GET | `/affiliates` | Listar afiliados |
| GET | `/affiliates/{id}` | Ver afiliado |
| PUT | `/affiliates/{id}` | Actualizar afiliado |
| DELETE | `/affiliates/{id}` | Desactivar afiliado |
| GET | `/affiliates/ref/{code}` | Resolver código de referido |
| GET | `/affiliates/generate-link/{id}` | Generar wa.me con ref_code |
| POST | `/earnings` | Registrar earning |
| GET | `/earnings` | Listar earnings |
| POST | `/payouts` | Solicitar pago |
| GET | `/payouts` | Listar pagos |
| POST | `/payouts/{id}/process` | Procesar pago |
| GET | `/affiliates/leaderboard` | Top afiliados |
| GET | `/affiliates/stats` | Estadísticas |

## Flujo de referido
1. Afiliado recibe su link wa.me con ref_code
2. Nuevo cliente hace clic y envía mensaje con el código
3. Sistema detecta el ref_code y crea earning para el afiliado
4. Afiliado ve sus earnings y solicita pago

## Uso

```bash
# Iniciar affiliates API
AFFILIATES_PORT=6400 python3 -m products.affiliates.main

# Crear afiliado
curl -X POST http://localhost:6400/affiliates \
  -H "Content-Type: application/json" \
  -d '{"name": "Carlos", "email": "carlos@ejemplo.com"}'

# Ver leaderboard
curl http://localhost:6400/affiliates/leaderboard
```
