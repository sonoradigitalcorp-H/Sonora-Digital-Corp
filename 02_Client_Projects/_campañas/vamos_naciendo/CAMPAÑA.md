# Campaña: VAMOS NACIENDO — Sonora Digital Corp (Lanzamiento)

**Estado**: 🟢 **LANZADA 2026-08-17** — 3 publicaciones en vivo (IG x2 + FB x1)
**Objetivo**: traer gente, llamar la atención, posicionar Sonora Digital Corp como la IA que automatiza PYMEs mexicanas. Engagement + leads + primer canal YouTube.
**Costo**: ~$0.15 total lanzamiento (imágenes FAL $0.05 c/u, video híbrido $0.05; todo lo demás $0).
**Canales**: Instagram + Facebook (reels) + YouTube (canal educativo TECNO SONORA, pendiente auth) + WhatsApp DM (leads) + Telegram (confirmación).
**Modo**: APROBACIÓN HUMANA — todo se confirma por WhatsApp (+5216623538272) y bot personal (@sonora_digital_bot) antes de publicar.

## Estrategia (clonada de los mejores creadores IA 2026)

1. **Hook 1-3s** (pregunta/pattern interrupt) — la primera frase decide el swipe.
2. **Antes/después** ("6 horas escribiendo copy → 12 minutos") — 4-5x outperform.
3. **Video domina**: 78-100% de los mejores posts son video.
4. **Comment-gating**: pedir comentar una palabra → 2-3x comentarios.
5. **Series numeradas** → 40%+ engagement (serie "X días con IA").
6. **Captions <100 palabras**.
7. **Probar 5 variantes, escalar ganador** (A/B en hooks).
8. **NUNCA fotos stock**: assets reales FAL + branding SDC (púrpura #6A0DAD / dorado #C9A227).
9. **Sin avatares ni lipsync** (por ahora): video híbrido imagen + voz Dalia + subtítulos.

## Pipeline video híbrido (por reel, $0.05)

```bash
# 1. Guion (hook 1-3s, <100 palabras, CTA wa.me/5216623538272)
# 2. Voz: edge-tts es-MX-DaliaNeural  ($0)
edge-tts --voice es-MX-DaliaNeural --text "$(cat guion.txt)" --write-media voz.mp3
# 3. Imagen FAL 1080x1920 ($0.05) — SIN texto (texto va en drawtext/subtítulos)
python3 ~/.hermes/skills/sdc/sdc-ai-content-engine/scripts/gen_fal.py image "<prompt>" img.jpg
# 4. Componer (duración = duración audio, ffmpeg wrapper ~/.local/bin)
~/.local/bin/ffmpeg -loop 1 -i img.jpg -i voz.mp3 -vf "scale=1080:1920,fps=25" -t <dur> -c:v libx264 -pix_fmt yuv420p -c:a aac -b:a 128k reel.mp4 -y
```

## Equipo (agentes/skills/MCPs)

| Rol | Skill/Herramienta | Acción |
|---|---|---|
| Estrategia | `sdc-content-strategy` | clonar Miguel Baena, Harper Carroll, Julian Goldie, Karol Życzkowski |
| Imagen | `gen_fal.py` (flux/dev) | $0.05, 1080x1920, sin texto |
| Video híbrido | `sdc-hybrid-video` + ffmpeg | imagen + voz Dalia + composición |
| Publicación IG/FB | Composio MCP (workspace sonoradigitalcorp) | INSTAGRAM_POST_IG_USER_MEDIA, FACEBOOK_* |
| YouTube | Composio (auth pendiente) | upload videos educativos |
| Confirmación | wacli CLI + Telegram API | WhatsApp dueño + bot @sonora_digital_bot |
| Voz | edge-tts es-MX-DaliaNeural | voz de marca SDC |
| CRM/leads | people.json + state.db + citas.db | cada lead su espacio, nunca olvidado |
| Memoria | Engram MCP | trazabilidad total |

## Assets (naming: campana_para_quien_tema)

| Archivo | Para quién | Tema | Estado |
|---|---|---|---|
| vn_reel01_lead_pyme_holograma_ia.jpg | PYMEs | empresaria + IA holograma | ✅ generado $0.05 |
| vn_reel02_lead_restaurante_whatsapp_ia.jpg | Restaurantes | dueño + WhatsApp IA | ✅ generado $0.05 |
| vn_reel01_pyme_ia.mp4 | PYMEs | reel 26s híbrido | ✅ compuesto $0.05 |

## Canal YouTube: TECNO SONORA (pendiente auth)

- Formato: solo video con texto y audio (sin avatar, sin lipsync)
- Contenido: enseñanza de nuevas tecnologías (agentes IA, automatización, herramientas)
- Cadencia: 3 videos/semana (lun/mié/vie)
- Pipeline: script → voz Dalia → imagen FAL/thumbnails → ffmpeg → upload vía Composio
- Series: "X días con IA" (40%+ engagement según expertos)

## Próximos pasos

1. 🟢 **PUBLICADO IG**: Reel PYMEs `18000883868995362` + Imagen restaurantes `18103504880461581` (https://www.instagram.com/p/DcKZTEJm7Qs/) — 2026-08-18 01:07 UTC
2. 🟢 **PUBLICADO FB**: Video post `1250923930445995` (page 996764866861279)
3. ⏳ Autorizar YouTube (link por WhatsApp) → subir Episodio 1 TECNO SONORA (yt_ep01_agentes_ia.mp4, 44.76s)
4. ⏳ Monitorear engagement + responder comentarios (comment-gating "Comenta IA")
5. Dashboard personal: cada lead tiene su espacio (people.json + state.db)
6. Cron 7am: reporte redes al dueño
7. Cron 6am: resumen verdades/mentiras