# SPEC — Content AI Pipeline Unificado

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260710-001` |
| **Fecha** | 2026-07-10 |
| **Autor** | Mystic (AI Agent) |
| **Tier** | 2 |
| **Estado** | completado |
| **Score requerido** | >=60 |

## 1. Objetivo

Unificar content generation pipeline (FAL, Muapi, edge-tts) con storage persistente local,
webhook delivery, y corrección de bugs críticos en edge-tts-server.

## 2. Value Driver

**founder-independence**: Elimina dependencia de URLs temporales de FAL/Muapi que expiran.
**automation**: Webhooks + cron cleanup reemplazan gestión manual de archivos.
**cost**: Storage local $0 (nginx + filesystem) vs S3/MinIO.
**reliability**: URLs persistentes, sin errores de hash no determinista.

## 3. Functional Requirements

| FR# | Descripción | Estado |
|-----|-------------|--------|
| FR1 | Fix hash no determinista en edge-tts-server | ✅ |
| FR2 | Fix return inválido (tupla en FastAPI) | ✅ |
| FR3 | Public HOST configurable via env var | ✅ |
| FR4 | Storage persistente local para imágenes | ✅ |
| FR5 | Storage persistente local para audio | ✅ |
| FR6 | Storage persistente local para video | ✅ |
| FR7 | nginx static serving en :8768 | ✅ |
| FR8 | Webhook registration tool | ✅ |
| FR9 | Webhook delivery automático post-generación | ✅ |
| FR10 | Cron cleanup de archivos >30 días | ✅ |
| FR11 | Migración DB (2 tablas nuevas + 3 columnas) | ✅ |
| FR12 | Google MCP removal | ✅ |
| FR13 | Open Notebook deployment | ✅ |
| FR14 | VPS cleanup (26 GB reclaimed) | ✅ |

## 4. Success Criteria

- [x] edge-tts genera filenames deterministas (mismo texto = mismo filename)
- [x] nginx sirve archivos estáticos en :8768 con CORS
- [x] Cada generación se descarga y persiste localmente
- [x] Webhook se dispara después de cada generación exitosa
- [x] Cleanup cron instalado y ejecutable
- [x] Content DB tiene tablas webhooks + deliveries
- [x] VPS disk bajó de 71% a 44%

## 5. Files Changed

| File | Cambio |
|------|--------|
| `products/content-studio/server.py` | +_download_to_local, persist, webhooks |
| `products/content-studio/edge-tts-server.py` | Fix 3 bugs |
| `products/content-studio/migrations/002_storage_webhooks.sql` | Nueva migration |
| `infra/docker-compose.products.yml` | +storage volume, -google-mcp, +open-notebook |
| `config/mcp/mcp-ecosystem.json` | -google-mcp, -notebooklm, +open-notebook |
| `~/.hermes/config.yaml` | -google-mcp, -notebooklm, +open-notebook |
| `scripts/ver.sh` | +open-notebook, +open-notebook-api |
| `AGENTS.md` | +open-notebook, +8768 storage, -google-mcp |

## 6. Architecture

```
FAL/Muapi/edge-tts → download → /data/content/{type}/{artist}/{uuid}.{ext}
                                     ↓
                               nginx :8768 (static serving)
                                     ↓
                              http://149.56.46.173:8768/{path}
                                     ↓
                              DB record (generations.output_urls)
                                     ↓
                              Webhook POST → artist endpoint
```
