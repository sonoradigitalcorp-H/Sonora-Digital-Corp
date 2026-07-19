# 🎙️ Sonora Marketing Audio

**8 audios profesionales** para tu marketing personal y de Sonora Digital Corp.

## Audios disponibles

| Archivo | Voz | Duración | Tema |
|---------|-----|----------|------|
| `audio/intro.mp3` | Dalia (MX, femenina) | ~51s | Presentación de marca |
| `audio/services.mp3` | Dalia (MX, femenina) | ~54s | Servicios |
| `audio/mystic.mp3` | Dalia (MX, femenina) | ~42s | Conoce a Mystic |
| `audio/founder.mp3` | Dalia (MX, femenina) | ~55s | Visión de Luis Daniel |
| `audio/whatsapp-demo.mp3` | Dalia (MX, femenina) | ~46s | Demo WhatsApp Agent |
| `audio/intro-masculino.mp3` | Jorge (MX, masculino) | ~51s | Presentación (voz hombre) |
| `audio/founder-masculino.mp3` | Jorge (MX, masculino) | ~55s | Visión (voz hombre) |
| `audio/mystic-espanola.mp3` | Elvira (ES, femenina) | ~42s | Mystic (acento español) |

## Cómo generar más

```bash
# Ver scripts disponibles
python3 -m products.marketing.generate --list

# Generar un audio específico con voz personalizada
python3 -m products.marketing.generate --script services --voice es-MX-JorgeNeural

# Generar todos
python3 -m products.marketing.generate --all
```

## Voces disponibles

- `es-MX-DaliaNeural` — Mexicana, femenina, profesional (recomendada)
- `es-MX-JorgeNeural` — Mexicana, masculina, seria
- `es-ES-AlvaroNeural` — Española, masculina, neutral
- `es-ES-ElviraNeural` — Española, femenina, cálida
- `es-US-AlonsoNeural` — Latinoamericana, masculina
