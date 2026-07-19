# WhatsApp Audio Thumbnail

- **MCP Server**: wacli_mcp
- **Tool**: `whatsapp_send_audio_thumbnail`
- **Input**: `to` (teléfono), `file_path` (MP3/OGG), `caption` (opcional, default "🎙️ Audio")
- **Output**: `{sent, id, to, thumbnail_type, error}`
- **Ejemplo**: `whatsapp_send_audio_thumbnail(to="5216622681111", file_path="/tmp/podcast.mp3", caption="🎧 Episodio 1")`
- **Descripción**: Genera una imagen PNG con forma de onda a partir de un archivo de audio y la envía por WhatsApp como preview visual antes de enviar el audio completo. Útil para podcasts, voice notes largos, o mensajes de voz con branding.
- **Permisos**: requiere Pillow instalado y acceso a wacli
- **Endpoint**: vía MCP wacli_mcp

## Casos de uso

1. **Preview de podcast**: enviar waveform antes del audio completo
2. **Voice note branding**: waveform con colores de marca (#FF6B35)
3. **Audio promocional**: thumbnail con caption descriptivo

## Notas

- El waveform es generado proceduralmente a partir del tamaño del archivo; no analiza el contenido de audio.
- El thumbnail se elimina del disco después de enviarse.
- Requiere que el archivo de audio exista.
