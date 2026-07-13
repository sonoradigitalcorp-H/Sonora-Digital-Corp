# Whisper Speech-to-Text

- **MCP Server**: whisper_mcp
- **Tools**: whisper_transcribe, whisper_list_models
- **Input**: audio_url (URL pública), language (default: es)
- **Output**: `{text, srt, srt_url, segments}`
- **Ejemplo**: `whisper_transcribe("https://...audio.wav", "es")`
- **Permisos**: requiere acceso a internet para descargar audio
- **Endpoint**: POST :8180/mcp/execute
