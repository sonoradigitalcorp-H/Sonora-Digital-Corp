# Campaña: 100 Seguidores — Sonora Digital Corp

**Objetivo**: conseguir 100 seguidores orgánicos en Instagram de sonoradigitalcorp (hoy tiene 2). Meta: 25 seguidores/semana × 4 semanas.
**Costo máximo**: $0.50/semana (solo 2-3 assets FAL; todo lo demás $0 local).
**Canal**: Instagram (sonoradigitalcorp) + WhatsApp (wacli, wa.me/5216623538272).

## Estrategia (clonada de los mejores)

1. **Seguir a PyMEs de Sonora** (perfil público, negocio visible) → muchos te siguen de vuelta. Fuente: topsearch por nicho (dentista/restaurante/bienes raíces hermosillo/obregón/nogales).
2. **Publicar 3 assets/semana** que muestren "cómo se vería tu negocio con IA" (imagen FAL + guion + voz). Ese es el gancho que el usuario pidió: **imágenes listas de cómo se vería su empresa**.
3. **Comment-gating**: cada post pide comentar 1 palabra ("comenta IA").
4. **DM a los que comentan o interactúan** (máx 10/día) con demo gratis + CTA wa.me.
5. **Responder comentarios** con Composio (máx 20/día).

## Equipo (agentes/skills/MCPs involucrados)

| Rol | Skill/Agente/MCP | Acción |
|---|---|---|
| Prospección | `sdc-ig-autopilot` + `sdc-campaigns/prospect.py` | buscar PyMEs, seguir (30/día) |
| Contenido | `sdc-ai-content-engine` (gen_fal.py) + `sdc-thumbnails` | 3 assets/semana (imagen/thumbnail) |
| Guion | `sdc-scripts` | hooks + antes/después + CTA |
| Video híbrido | `sdc-hybrid-video` | imagen + voz Dalia + ffmpeg ($0.05) |
| Publicación | `sdc-instagram-composio` (Composio) | POST_IG_USER_MEDIA + PUBLISH |
| DM/Follow | `sdc-ig-autopilot` (Playwright) | DMs (10/día), follows (30/día) |
| Respuesta | Composio `INSTAGRAM_POST_IG_MEDIA_COMMENTS` | responder comentarios (20/día) |
| Onboarding/venta | `sdc-wacli` + `sdc-onboarding` | responder leads que llegan por wa.me, hacer demo |
| Voz | edge-tts `es-MX-DaliaNeural` | narración de videos |
| Memoria/trazabilidad | Engram MCP (`sdc-engram`) | registrar progreso |

## Plan semanal determinista (repetir 4 semanas)

**Lunes**: `discover --query "<nicho>" --limit 30` → guardar prospects. Elegir 3 candidatos para contenido de la semana.
**Mar-jue**: generar 3 assets (1 imagen FAL $0.05 + 2 recomposiciones de thumbnail/guion $0). Publicar con Composio. Programar seguimiento.
**Vie**: `follow --limit 25 --execute` (rate limit 30). Responder comentarios con Composio.
**Sab**: `dm --limit 8 --execute` a los que interactuaron (máx 10/día). CTA demo wa.me.
**Dom**: análisis con `INSTAGRAM_GET_USER_INSIGHTS` → ajustar nicho/guión para la siguiente semana.

## Métricas objetivo (semana 1)

- Seguidos por nosotros: 25-30 (límite humano 30/día)
- Seguidores ganados: +25
- Comentarios recibidos: 5-15 (comment-gating)
- DMs enviados: 10 (tope) → 3-5 respuestas → 1-2 demos wa.me
- Costo: ~$0.15 (3 imágenes FAL)

## Archivos

- Prospects: `~/.hermes/campaigns/prospects.json`
- Thumbnails: `00_Administration/Content/Thumbnails/100_seguidores/`
- Guiones: `00_Administration/Content/Scripts/100_seguidores/`
