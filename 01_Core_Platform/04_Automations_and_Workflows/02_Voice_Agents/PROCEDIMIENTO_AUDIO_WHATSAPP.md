# Procedimiento Estándar: Envío de Audio por WhatsApp (Pipeline Local)

## Propósito
Documentar el proceso estándar para generar audio TTS localmente, convertirlo a formato WhatsApp (OGG Opus), y enviarlo por WhatsApp usando únicamente herramientas locales.

## Herramientas Requeridas (Todas Locales)

| Herramienta | Función | Ubicación | Estado |
|-------------|---------|-----------|--------|
| `edge-tts` | Genera audio TTS a partir de texto | npm global | ✅ Instalado |
| `ffmpeg` | Convierte audio entre formatos (fallback) | `/usr/bin/ffmpeg` | ⚠️ Problema con libva |
| Python + soundfile | Convierte MP3 → OGG Opus (alternativa) | `python3` | ✅ Funcional |
| `wacli` | Envía mensajes y archivos por WhatsApp | `~/.local/bin/wacli` | ✅ Instalado |
| `opus-tools` | Codifica audio Opus | `opusenc` | ✅ Instalado |

## Pipeline Completo

### Paso 1: Crear el guión de audio

Guardar el texto del guión en un archivo `.txt`:

```bash
# Ejemplo: /home/mystic/Documentos/Sonora Digital Corp Nuevo/guion_sergio.txt
```

### Paso 2: Generar audio MP3 con edge-tts

```bash
edge-tts \
  --voice es-ES-AlvaroNeural \
  --file "/ruta/al/guion.txt" \
  --write-media "/ruta/al/audio.mp3"
```

**Nota:** `es-ES-AlvaroNeural` es la voz masculina española. Para voz femenina usar `es-ES-ElviraNeural`.

### Paso 3: Convertir MP3 a OGG Opus (Formato WhatsApp PTT)

#### Opción A: ffmpeg (si funciona)
```bash
ffmpeg -y -i "audio.mp3" -c:a libopus -b:a 16k -ar 16000 "audio.ogg"
```

#### Opción B: Python con soundfile (recomendada)
```bash
python3 -c "
import soundfile as sf
data, sr = sf.read('audio.mp3')
sf.write('audio.ogg', data, sr, format='OGG', subtype='OPUS')
"
```

**Requisitos:** `pip install soundfile`

### Paso 4: Enviar por WhatsApp con wacli

#### 4.1 Verificar autenticación
```bash
wacli auth status --store ~/.config/ai.opencode.desktop/wacli --json
```

Si retorna `{"authenticated": false}`, proceder al paso 4.2.

#### 4.2 Autenticar wacli (QR)
```bash
wacli auth --qr-format text --store ~/.config/ai.opencode.desktop/wacli
```

Escanear el QR con WhatsApp móvil:
**Configuración → Dispositivos vinculados → Vincular un dispositivo**

#### 4.3 Enviar audio como nota de voz (PTT)
```bash
wacli send file \
  --store ~/.config/ai.opencode.desktop/wacli \
  --to "521XXXXXXXXXX@s.whatsapp.net" \
  --file "/ruta/al/audio.ogg" \
  --mime "audio/ogg; codecs=opus" \
  --ptt \
  --post-send-wait 5s
```

**Notas:**
- Formato del número: `521` + número de 10 dígitos + `@s.whatsapp.net`
- Ejemplo Sergio: `5216624707325@s.whatsapp.net`
- La flag `--ptt` envía como nota de voz (push-to-talk)
- `--post-send-wait 5s` espera confirmación de entrega

## Ejemplo Completo (Caso Sergio)

```bash
# 1. Guión ya creado en:
GUION="/home/mystic/Documentos/Sonora Digital Corp Nuevo/guion_sergio.txt"

# 2. Generar audio MP3
edge-tts --voice es-ES-AlvaroNeural --file "$GUION" \
  --write-media "/tmp/audio_sergio.mp3"

# 3. Convertir a OGG Opus
python3 -c "
import soundfile as sf
data, sr = sf.read('/tmp/audio_sergio.mp3')
sf.write('/tmp/audio_sergio.ogg', data, sr, format='OGG', subtype='OPUS')
"

# 4. Enviar por WhatsApp
wacli send file --store ~/.config/ai.opencode.desktop/wacli \
  --to "5216624707325@s.whatsapp.net" \
  --file "/tmp/audio_sergio.ogg" \
  --mime "audio/ogg; codecs=opus" \
  --ptt \
  --post-send-wait 5s
```

## Troubleshooting

### ffmpeg falla con libva
**Síntoma:** `symbol lookup error: libva-x11.so.2: undefined symbol: va_fool_postp`
**Solución:** Usar la conversión con Python/soundfile (Paso 3, Opción B)

### wacli no autenticado
**Síntoma:** `not authenticated; run 'wacli auth'`
**Solución:** Ejecutar `wacli auth --qr-format text` y escanear el QR con WhatsApp móvil

### audio.ogg no se envía
**Verificar:**
1. El archivo existe y tiene tamaño > 0
2. El formato MIME es exactamente: `audio/ogg; codecs=opus`
3. La flag `--ptt` está presente
4. El número tiene formato correcto: `521XXXXXXXXXX@s.whatsapp.net`

## Archivos Generados en esta Ejecución

| Archivo | Ubicación | Descripción |
|---------|-----------|-------------|
| `guion_sergio.txt` | `/home/mystic/Documentos/Sonora Digital Corp Nuevo/guion_sergio.txt` | Guión del audio |
| `audio_sergio.mp3` | `/home/mystic/Documentos/Sonora Digital Corp Nuevo/audio_sergio.mp3` | Audio TTS (959 KB) |
| `audio_sergio.ogg` | `/home/mystic/Documentos/Sonora Digital Corp Nuevo/audio_sergio.ogg` | Audio convertido a OGG Opus |

## Referencias

- **wacli SKILL.md:** `/home/mystic/.openclaw/extensions/whatsapp/skills/wacli/SKILL.md`
- **openclaw gateway:** `http://localhost:18789`
- **wacli store:** `~/.config/ai.opencode.desktop/wacli`
- **Número de cuenta WhatsApp:** 5216623538272

---

**Última actualización:** 2026-08-05
**Versión:** 1.0
**Autor:** Pipeline Automático de Audio WhatsApp
