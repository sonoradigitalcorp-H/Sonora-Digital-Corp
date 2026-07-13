# FFmpeg Video Editing

- **MCP Server**: ffmpeg_mcp
- **Tools**: ffmpeg_convert, ffmpeg_multiformat
- **Input**: video_url + target (convert), video_url + artist_name (multiformat)
- **Output**: `{url, format}` (convert), `{urls: {tiktok, reels, shorts, facebook}}` (multiformat)
- **Ejemplo**: `ffmpeg_multiformat("https://...video.mp4", "Hector Rubio")`
- **Permisos**: requiere FFmpeg instalado en el sistema
- **Endpoint**: POST :8180/mcp/execute
