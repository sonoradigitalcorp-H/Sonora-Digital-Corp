# ABE Studio — Specification v1.0.0

**Value**: Generación automatizada de video IA para artistas musicales
**Eventos**: generation.requested, generation.completed, generation.failed, credits.low
**Pipeline**: VDD → EDD → SDD → TDD

## Capacidades

1. **Prompt Reels** — Text-to-Video: prompt → video 5-15s
2. **Foto Reels** — Image-to-Video: foto + prompt → video animado
3. **Beat Sync** — Audio-driven: canción + foto → video sincronizado
4. **Clone Studio** — Reference-to-Video: @character + prompt → video consistente
5. **Lyric Flow** — Letra animada (Seedance + overlay)
6. **ABE Cuts** — Multi-clip pipeline (encadenar 15s → 1min+)

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | /studio/generate | Crear tarea de generación |
| GET | /studio/tasks/:id | Estado de tarea |
| GET | /studio/artists | Listar artistas con @character |
| POST | /studio/artists/:id/character | Configurar @character |
| GET | /studio/credits | Saldo de créditos |
| POST | /studio/webhook | Callback de Seedance |
| GET | /studio/history | Historial de generaciones |

## Eventos

- `generation.requested` → encolar en Redis
- `generation.completed` → notificar usuario + guardar video
- `generation.failed` → reintentar o marca fallido
- `credits.low` → alertar (< 20% saldo)
- `monthly.reset` → resetear contadores

## Reglas de Negocio

- Básico: 5 reels/mes, 720p, solo T2V
- Pro: 20 reels/mes, 1080p, I2V + audio
- Elite: ilimitado, 1080p, reference-to-video
- Videos expiran en CDN → descargar a storage local
- @character necesita 3-5 fotos del artista
