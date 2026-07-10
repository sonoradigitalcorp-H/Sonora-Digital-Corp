# Products — Sonora Digital Corp

Cada subdirectorio es un producto autocontenido:

| Producto | Puerto | Stack |
|---|---|---|
| `content-studio/` | 8765, 8766 | Python, asyncpg, edge-tts, FAL API |
| `google-mcp/` | 8767 | Python, MCP, Gemini API |
| `omnivoice/` | 3900 | OmniVoice Studio (Docker image) |

## Reglas

1. Cada producto tiene su propia DB en Postgres (`sdc_content`, `sdc_social`, etc.)
2. Cada producto tiene su propio `docker-compose.yml` (usa `external: true` para `sdc-network`)
3. Productos se comunican con core OS vía MCP/HTTP, nunca Python imports directos
4. Para iniciar todo: `scripts/up.sh`
5. Para iniciar solo core: `docker compose -f infra/docker-compose.yml up -d`
6. Para iniciar solo productos: `docker compose -f infra/docker-compose.products.yml up -d`
