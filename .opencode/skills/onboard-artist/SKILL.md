---
name: onboard-artist
description: >
  Wizard para registrar un nuevo artista en ABE Music Group.
  Crea su perfil, configura split, conecta collectors,
  y opcionalmente activa voz.
license: MIT
compatibility: opencode
metadata:
  domain: music
  capabilities: crm, onboarding, artists
---

## Qué hace

Guía el proceso completo de registro de un nuevo artista:
- Recopila información del artista
- Crea archivo de perfil en clients/abe-music/artists/
- Configura split de regalías
- Conecta collectors (Spotify, YouTube)
- Opcional: activa voz para el artista

## Cuándo usarlo

- Cuando se firma un nuevo artista
- Cuando Luis Daniel dice "onboard"

## Pasos

1. **Recopilar información**
   - Preguntar: nombre artístico, nombre real, género, redes
   - Preguntar: split deseado (default 70/20/10)
   - Preguntar: ¿quiere asistente de voz?

2. **Crear perfil**
   - Generar clients/abe-music/artists/<artist-id>.yml
   - Incluir: nombre, género, split, redes sociales, estado

3. **Conectar collectors**
   - Si tiene Spotify ID, conectar collector
   - Si tiene YouTube, conectar collector

4. **Activar voz (opcional)**
   - Si aplica, ejecutar skill deploy-voice

5. **Confirmar**
   - Mostrar resumen de lo creado
   - "Artista X activado. Voz: sí/no. Collectors: Spotify, YouTube."

## Template de perfil

```yaml
# clients/abe-music/artists/example.yml
id: example
name: "Nombre Artístico"
real_name: "Nombre Real"
genre: "Género Musical"
status: active
split:
  artist: 70
  label: 20
  reserve: 10
signed_date: 2026-07-11
social:
  spotify_id: "..."
  youtube_id: "..."
  instagram: "@..."
voice_assistant: false
```
