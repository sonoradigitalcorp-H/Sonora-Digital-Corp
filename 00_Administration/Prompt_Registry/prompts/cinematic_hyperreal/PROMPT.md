# PROMPT — cinematic_hyperreal v1.0.0
**Estado:** test · **Judge:** pendiente · **Fecha:** 2026-08-13

## Plantilla canónica (imagen — FAL flux/dev)

```
PROMPT_BASE (imagen):
Photorealistic cinematic photograph, golden-hour rim light, shallow depth of field f/1.8,
shot on 35mm, editorial composition, rule of thirds, high detail skin and fabric texture,
warm color grade with subtle blue-and-gold accent. Subject: {SUJETO}. Background: {CONTEXTO}
softly blurred. No text in image. 1080x1920 portrait, realistic, 8k quality, professional.

{sujeto_detalle}
{contexto_detalle}
{adicionales}
```

### Controles de guion (reemplazar los placeholders)

| Variable | Descripción | Ejemplo |
|---|---|---|
| `{SUJETO}` | Rol visual principal | "un agente IA representado como asistente digital elegante flotando" |
| `{CONTEXTO}` | Escenario del nicho (desenfocado) | "cocina de restaurante con mesas iluminadas" |
| `{sujeto_detalle}` | Dirección de actuación/pose | "sentado, viendo una tableta con chat de WhatsApp, sonrisa serena" |
| `{contexto_detalle}` | Objetos de apoyo | "manteles blancos, copas, fondo de cocina con vapor" |
| `{adicionales}` | Mood/luz extra o restricción | "NO manos deformadas, NO texto, lente 35mm" |

## Plantilla canónica (video — FAL ltx-video)

```
PROMPT_BASE (video):
Cinematic hyperreal video, slow stable camera, minimal motion, {SUJETO} in {CONTEXTO},
golden-hour lighting, shallow depth of field, warm grade with blue-gold accent,
professional 9:16 composition, no text. num_frames<=64, costo<=$0.50.
```

## Reglas de guion (deterministas)

1. SIEMPRE incluir: luz dorada O rim light + shallow DOF + encuadre editorial.
2. SIEMPRE: "No text in image" (el texto se añade en edición).
3. SIEMPRE: costo implícito <= $0.50 (flux/ltx/kling) — nunca modelos caros.
4. NUNCA: "persona sonriendo genérica" sin contexto (aburre, no para scroll).
5. Para personas: NUNCA qwen2.5vl local para describir — usar OpenRouter qwen-2.5-vl-72b.
6. Movimiento en video: mínimo y contenido (reduce flickering, sube quality).
7. 1 imagen por operación; video num_frames<=64.

## Anti-guiones (lo que NUNCA debe producir)
- "generic smiling person" sin contexto de negocio.
- Manos deformadas / dedos extra → añadir "NO deformed hands".
- Texto legible → añadir "No text in image".
- Aspecto plastificado → "high detail texture, not plastic".
