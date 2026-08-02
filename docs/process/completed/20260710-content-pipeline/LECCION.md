# LECCION — Content AI Pipeline Unificado

## Errores

| # | Error | Impacto | Lección |
|---|-------|---------|---------|
| 1 | `hash()` en edge-tts-server | Filenames no deterministas entre procesos | Usar `hashlib.md5()` para persistencia de cache |
| 2 | `return {"error"}, 404` en FastAPI | Error 500 en vez de 404 | FastAPI espera `raise HTTPException(404)` |
| 3 | `localhost` hardcodeado en URLs | Inaccesible desde otros servicios | Usar env var `PUBLIC_HOST` |
| 4 | Volumen duplicado `omnivoice-data` (3GB) | 3GB perdidos por semanas | Verificar nombres al migrar docker run → compose |
| 5 | `sdc_*` volumes del compose anterior | 10 volúmenes huérfanos (700MB) | Usar `--project-name` consistente |
| 6 | `networks:` reemplazado por `volumes:` en YAML | Compose falló al hacer up | Revisar estructura YAML después de editar |

## Aciertos

| # | Acierto | Por qué |
|---|---------|---------|
| 1 | Storage local con nginx | $0, 0 containers extra, nginx ya instalado |
| 2 | `_download_to_local()` genérica | Reutilizable para imágenes, audio, video, OCR |
| 3 | Webhooks con delivery tracking | Postgres registra cada intento + código respuesta |
| 4 | `asyncio.create_task()` para webhooks | No bloquea el pipeline principal |
| 5 | Cron cleanup + columnas file_size/file_type | Auto-mantenimiento del storage |
| 6 | latest-single image de Open Notebook | SurrealDB embebido, sin otro container |

## Incompleto / Pendiente

| # | Tema | Por qué quedó |
|---|------|---------------|
| 1 | LoRA real (conectar use_lora a FAL) | Requiere test con FAL LoRA endpoint |
| 2 | Voice cloning real (OmniVoice API) | OmniVoice deshabilitado en Hermes |
| 3 | OCR tool (EasyOCR) | No se instaló el paquete |
| 4 | Image editing (FAL flux-fill-pro) | Nuevo MCP tool necesario |
| 5 | Avatar interactivo real-time | Requiere pipeline Whisper→DeepSeek→TTS→Muapi |
| 6 | SPEC formal para Content AI Pipeline | Se documentó como Tier 2 sin pipeline completo |
| 7 | Sync cron del repo | Script existe pero no está instalado |
