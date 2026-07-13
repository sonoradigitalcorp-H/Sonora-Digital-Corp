# OmniVoice

- **MCP Server**: omnivoice_mcp
- **Tools**: omnivoice_speak, omnivoice_clone, omnivoice_list_voices
- **Input**: text (speak), audio_url+name (clone)
- **Output**: `{audio_url}` o `{profile_id}`
- **Ejemplo**: `omnivoice_speak("Hola fans", "cloned_hector", "es")`
- **Permisos**: servicio interno
- **Endpoint**: POST :8180/mcp/execute
