# COORDINACIÓN MULTI-AGENTE — 2026-08-10

> Handshake para cualquier agente (Gemini / Claude / OpenCode / futuro). Leer ANTES de trabajar.

## Estado base (única fuente de verdad)

- **HEAD**: `15b817c` — chore: embeddings dual VPS+local, estructura limpia, bots Aztrotech + skills
- **Rama**: `master` (local, no pusheada a `next`)
- **Working tree**: LIMPIO (solo sin trackear: datos clientes + .playwright-mcp — NO TOCAR, ver abajo)
- **ESTADO.md**: actualizado 2026-08-10 con embeddings dual + MCP server movido

## Zonas de NO TOQUE (protegidas)

| Ruta | Por qué | Regla |
|---|---|---|
| `01_Core_Platform/03_Agentic_Infrastructure/Databases/Aztrotech_Citas/` | Datos VIVOS del bot (citas.db, voz.db, leads/) | NO borrar, NO mover, NO commitear |
| `01_Core_Platform/03_Agentic_Infrastructure/Hermes_Agent/Databases/` | MISMO storage (bind mount/espejo inodos idénticos) | Espejo de la carpeta de arriba — tocar = duplicar riesgo. NO tocar |
| `.playwright-mcp/` | Logs viejos de navegador MCP | Ignorar (candidato a .gitignore) |
| `main` / rama `next` en GitHub | CI/CD despliega a VPS producción | NUNCA push directo sin OK de MYSTIC |
| VPS 187.124.85.191 (producción) | Usuarios reales Nathaly/Marco/TripleR | Solo cambios con OK explícito |

## Infra del sistema (para contexto rápido)

- **Embeddings**: `all-minilm` 384-dim. LOCAL Ollama (127.0.0.1:11434, systemd) + VPS OVH (149.56.46.173:11434) como fallback. `OLLAMA_ENDPOINT` en ~/.hermes/.env
- **Qdrant**: localhost:6333, colecciones por tenant (tenant_aztrotech, kb_rye, hermes...). API: colecciones anidadas en `result.collections`
- **Postgres**: `sdc:sdc_local_dev@localhost:5432/sdc`. Tabla `contacts`
- **Modelo LLM**: `openrouter/deepseek/deepseek-v4-flash-0731` (único con créditos, key en ~/.hermes/.env)
- **Ollama local**: `ollama.service` activo, modelos: `all-minilm` (45MB), `tinyllama:1.1b`, `nomic-embed-text` (768-dim — NO usar con Qdrant 384)

## Cómo colaborar sin pisarse

1. **Leer ESTADO.md completo** antes de proponer cualquier cambio
2. **Un cambio a la vez**: si algo ya está en progreso (git status sucio), termínalo antes de empezar otro
3. **Commit pequeño y atómico** con mensaje que describa el qués/por qué. Verificar con `bash 00_Administration/guardians/structure_guard.sh` (debe decir VERDE)
4. **Nunca commitear secretos** (grep `sk-or-|api[_-]?key|token` antes)
5. **Guardar en Engram** (mem_save) cualquier decisión/discovery importante → el otro agente lo ve vía mem_context
6. **No crear procesos paralelos** que compitan por el mismo bot token (lección aprendida: 409 conflict / CPU 100%)
7. Ante duda entre dos opciones → elegir la que NO rompa lo existente y documentar

## Flujo recomendado cuando trabajas a la par

```
1. Verifica no haber conflicto: git log -1, git status --short, structure_guard.sh
2. Busca en Engram si ya se resolvió (mem_search)
3. Ejecuta TU parte (rápida, atómica)
4. Verifica (guard verde + sin secretos)
5. Commit chico + mem_save
6. Reporta en qué quedó tu parte (punto único de contacto: ESTADO.md)
```