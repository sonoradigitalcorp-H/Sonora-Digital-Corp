# System Tools

Tools del sistema para operaciones core. Incluye las 20 tools del antiguo `SkillAgent.SKILL_CATALOG`.

| Tool | Origen | Descripción |
|------|--------|-------------|
| files | `mcp/tools/files.js` + `apps/jarvis/src/core/tools/` | read_file, write_file, list_files |
| commands | `mcp/tools/commands.js` + `apps/jarvis/src/core/tools/` | execute_command |
| voice | `mcp/tools/voice.js` + `apps/voice/` | STT, TTS, wake word |
| memory | `apps/jarvis/src/core/tools/` (rag_store, search_semantic) | Memoria persistente |
| mcp | `SkillAgent: mcporter` | Gestión de servidores MCP |
| healthcheck | `SkillAgent: healthcheck` | Auditoría de seguridad y estado |
| search | `apps/jarvis/src/core/tools/` (search_code, search_semantic) | Búsqueda en código y vectores |
| tests | `apps/jarvis/src/core/tools/` (run_tests) | Ejecución de tests |
| docker | `apps/jarvis/src/core/tools/` (docker_build, docker_deploy) | Operaciones Docker |
| user | `apps/jarvis/src/core/tools/` (ask_user) | Interacción con usuario |
| web-fetch | `SkillAgent: web_fetch` | Obtener contenido de URLs |
| analyze-code | `SkillAgent: analyze_code` | Análisis de código fuente |
| skill-creator | `SkillAgent: skill_creator` | Crear nuevas skills |
| github | `SkillAgent: github` | Gestión GitHub |
| google | `SkillAgent: gog` | Google Workspace |
| taskflow | `SkillAgent: taskflow` | Tareas multi-paso |
| tts | `SkillAgent: sag` | Texto a voz (ElevenLabs) |
| browser | `SkillAgent: browser_use` | Control de navegador |
| desktop | `SkillAgent: linux_desktop` | Control de escritorio |
