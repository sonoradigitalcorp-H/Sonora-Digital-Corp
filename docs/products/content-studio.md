# Manual de Producto — Content Studio

## ¿Qué es?
Servicio MCP de generación de contenido: imágenes, TTS, talking heads, OCR, edición de imágenes. Corre en :8765.

## Tools disponibles (20)
| Tool | Descripción | Costo |
|------|-------------|-------|
| `generate_image` | Texto → imagen (fal-ai/flux-pro) | $0.05 |
| `generate_tts` | Texto → voz (edge-tts) | $0.00 |
| `generate_talking_head` | Foto + texto → video talking head | $0.08 |
| `generate_lip_sync` | Video + audio → lip sync | $0.06 |
| `generate_binaural` | Audio → binaural 3D | $0.03 |

Ver API.md completa en `products/content-studio/API.md`.

## Uso vía MCP
```json
{
  "tool": "generate_image",
  "params": { "prompt": "un artista tocando guitarra", "use_lora": true }
}
```

## Despliegue
```bash
docker compose -f infra/docker-compose.products.yml up -d content-server
```

## Almacenamiento
Archivos en `/home/ubuntu/data/content-studio/`. Servidos por nginx en :8768.
