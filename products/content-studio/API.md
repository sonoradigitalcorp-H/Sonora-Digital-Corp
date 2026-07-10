# Content Studio — API Reference

Content Studio expone **20 tools** via MCP SSE protocol en `http://<host>:8765/sse`.

## Conexión

```python
from mcp import ClientSession
from mcp.client.sse import sse_client

async with sse_client("http://149.56.46.173:8765/sse") as streams:
    async with ClientSession(streams[0], streams[1]) as session:
        await session.initialize()
        result = await session.call_tool("generate_image", {
            "prompt": "un artista cantando en estudio",
            "use_lora": True
        })
```

## Tools

### Imagen

| Tool | Args | Returns |
|------|------|---------|
| `generate_image` | `prompt`, `artist_id?`, `negative_prompt?`, `width?`, `height?`, `use_lora?` | `{provider, url, model}` |
| `edit_image` | `prompt`, `image_url`, `mask_url?`, `artist_id?` | `{provider, url}` |
| `register_lora_weights` | `artist_id`, `path`, `scale?` (0.8), `name?` | `{lora_weight_id}` |
| `list_lora_weights` | `artist_id?` | `[{id, name, path, scale}]` |
| `delete_lora_weights` | `weight_id` | `{status}` |

### Audio / Voz

| Tool | Args | Returns |
|------|------|---------|
| `text_to_speech` | `text`, `voice_id?`, `language?`, `provider?` | `{provider, url}` |
| `clone_voice` | `artist_id`, `audio_urls[]`, `name?`, `language?` | `{voice_profile_id, voice_id}` |

### Video

| Tool | Args | Returns |
|------|------|---------|
| `generate_talking_head` | `image_url`, `script?`, `audio_url?`, `provider?`, `artist_id?` | `{provider, url}` |

### OCR

| Tool | Args | Returns |
|------|------|---------|
| `ocr_image` | `image_url`, `language?` (es), `artist_id?` | `{text, entries[], char_count}` |

### Pipeline / Queue

| Tool | Args | Returns |
|------|------|---------|
| `queue_content` | `artist_id`, `prompt`, `media_type?`, `template_id?`, `platform?`, `nsfw?`, `schedule_hours?` | `{generation_id, queue_id}` |
| `process_queue` | `batch_size?` | `{processed: N}` |
| `get_generation_status` | `generation_id` | `{id, status, output_urls}` |

### Templates

| Tool | Args | Returns |
|------|------|---------|
| `list_templates` | `category?` | `[{id, name, category, virality_score}]` |
| `create_template` | `name`, `category`, `prompt_template`, `engine?`, ... | `{id, name}` |

### Administración

| Tool | Args | Returns |
|------|------|---------|
| `get_product_tiers` | — | `[{id, name, price_usd, has_lora, has_voice_clone}]` |
| `get_artist_summary` | `artist_id` | `{artist, generations}` |
| `list_artists` | — | `[{id, name, genre, streams, revenue}]` |

### Webhooks

| Tool | Args | Returns |
|------|------|---------|
| `register_webhook` | `artist_id`, `url`, `secret?`, `events?` | `{webhook_id}` |
| `list_webhooks` | `artist_id?` | `[{id, url, events}]` |
| `delete_webhook` | `webhook_id` | `{status}` |

## Webhook Events

| Evento | Disparo |
|--------|---------|
| `generation.completed` | Después de generar y persistir contenido. Payload: `{event, generation_id, artist_id, url, media_type, platform}` |

## Storage

Los contenidos generados se almacenan en `/data/content/` y se sirven por nginx:

```
http://149.56.46.173:8768/images/<artist_id>/<uuid>.jpg
http://149.56.46.173:8768/audio/<artist_id>/<uuid>.mp3
http://149.56.46.173:8768/video/<artist_id>/<uuid>.mp4
http://149.56.46.173:8768/ocr/<artist_id>/<uuid>.txt
```

## Costos por Proveedor

| Proveedor | Modelo | Costo |
|-----------|--------|-------|
| FAL | flux-schnell | $0 (free tier) |
| FAL | flux-lora | $0 (free tier) |
| FAL | flux-fill-pro | $0 (free tier) |
| FAL | sadtalker | ~$0.01/video |
| Muapi | infinitetalk | ~$0.20/video |
| Muapi | creatify-lipsync | ~$0.04/video |
| edge-tts | — | $0 |
| OpenAI | tts-1 | ~$0.015/request |
| EasyOCR | — | $0 (local) |
| OmniVoice | — | $0 (local) |

## Endpoints Adicionales

| Endpoint | Método | Puerto | Descripción |
|----------|--------|--------|-------------|
| `/sse` | GET | 8765 | MCP SSE endpoint |
| `/messages/` | POST | 8765 | MCP tool calls |
| `/tts` | POST | 8766 | Edge TTS HTTP API |
| `:8768` | GET | 8768 | nginx static content |

## Docker

```bash
# Inicio rápido
docker compose -f docker-compose.yml up -d

# Variables de entorno requeridas
export FAL_KEY="<key>"
export MUAPI_KEY="<key>"
export OMNIVOICE_URL="http://omnivoice:3900"
```
