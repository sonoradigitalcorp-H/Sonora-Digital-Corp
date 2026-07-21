# Manual de Producto — OmniVoice

## ¿Qué es?
API de clonación de voz. Permite crear perfiles de voz personalizados desde muestras de audio y generar speech con esa voz.

## Acceso
- **API**: http://149.56.46.173:3900
- **Docker**: `ghcr.io/sonoradigitalcorp/omnivoice:latest`

## Uso

### Clonar voz
```bash
curl -X POST http://localhost:3900/profiles \
  -F "audio=@sample.wav" \
  -F "name=Mi Voz"
# → { "profile_id": "abc-123" }
```

### Generar speech
```bash
curl -X POST http://localhost:3900/synthesize \
  -H "Content-Type: application/json" \
  -d '{"profile_id": "abc-123", "text": "Hola mundo"}'
# → audio/wav
```

## Integración con Content Server
Usar `clone_voice` tool desde content-studio para clonar voces y almacenar profile IDs en DB.
