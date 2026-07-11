---
name: generate-content
description: >
  Pipeline de generación de contenido: research -> script -> video -> audio -> publish.
  Usa Content Studio API y OmniVoice para producción multimedia.
license: MIT
compatibility: opencode
metadata:
  domain: content
  capabilities: video, audio, social-media
---

## Qué hace

Ejecuta el pipeline completo de creación de contenido:
- Research: busca tendencias y noticias
- Script: escribe guión con IA
- Video: genera video con talking head o imágenes
- Audio: genera voz en off con TTS
- Publica: sube a redes sociales

## Cuándo usarlo

- Para contenido diario de redes
- Para promociones de artistas
- Cuando se activa el pipeline automático

## Pasos

1. **Research**
   - Buscar noticias/tendencias del artista o género
   - Identificar tema del día

2. **Escribir script**
   - Generar guión de 30-60 segundos
   - Adaptar al tono del artista

3. **Generar video**
   - Usar Content Studio API (:8765) para generar video
   - O usar Fal.ai para generación

4. **Generar audio**
   - Usar TTS (src/voice/tts.py) para voz en off
   - O usar OmniVoice (:3900) para clonar voz del artista

5. **Publicar**
   - Preparar post para cada red social
   - Usar @playwright/mcp para automatizar publicación

## Referencias

- Content Studio: products/content-studio/ (puerto :8765)
- OmniVoice: products/omnivoice/ (puerto :3900)
- TTS: src/voice/tts.py
