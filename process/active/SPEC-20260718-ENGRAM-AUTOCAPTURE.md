# SPEC-20260718-ENGRAM-AUTOCAPTURE
## Engram Auto-Capture System — Specification

### FR-01: Auto-Captura de Comandos Bash
**Dado** que el usuario ejecuta comandos en terminal
**Cuando** el comando coincide con patrones relevantes (git, npm, pip, docker, kubectl, make, rsync, scp, ssh, wacli, engram, python *.py)
**Entonces** el sistema guarda automáticamente una observación en Engram con:
- Título: `cmd: <primeros 60 chars>`
- Tipo: `command`
- Contenido: comando, directorio, exit code, timestamp
- Topic key: `commands/YYYYMMDD`
- Proyecto: detectado por cwd o ENGRAM_PROJECT

**Criterios de aceptación:**
- No captura comandos de solo lectura (ls, cat, grep, pwd, cd, echo)
- Latencia < 100ms por comando
- Rate limit: máx 30 obs/min por sesión
- Falla silenciosamente (no rompe el shell)

---

### FR-02: Snapshot de Variables de Entorno
**Dado** que inician/terminan sesiones o cambian configs críticas
**Cuando** se detecta cambio en vars con prefijos: SDC_, MCP_, OPENCLAW_, QDRANT_, NEO4J_, SUPABASE_, ABE_, WACLI_, ENGRAM_
**Entonces** guarda observación tipo `config` con JSON completo de vars relevantes
**Topic key:** `env/YYYYMMDD`

---

### FR-03: Snapshot de Estado Git
**Dado** commits, merges, rebases, o cambios en working tree
**Cuando** `git status --short` o `git diff --stat` cambia
**Entonces** guarda observación tipo `config` con:
- Status short
- Diff stat
- Últimos 5 commits (oneline)
**Topic key:** `git/YYYYMMDD`

---

### FR-04: Snapshot de Procesos Relevantes
**Dado** intervalo configurable (default 5 min) o evento de deploy/restart
**Cuando** escanea `ps aux`
**Entonces** filtra y guarda procesos con keywords: python, node, docker, postgres, redis, neo4j, qdrant, n8n, ollama, wacli, engram, openclaw
**Tipo:** `architecture`
**Topic key:** `processes/YYYYMMDD`

---

### FR-05: Versionado Semántico por Topic Key
**Dado** un topic_key (ej: `architecture/auth-model`)
**Cuando** se guarda una nueva observación con ese topic_key
**Entonces** el sistema calcula versión semántica:
- `revision_count` → `v{major}.{minor}.{patch}`
- major = revision_count // 100
- minor = (revision_count % 100) // 10
- patch = revision_count % 10
- Incluye en respuesta: `version`, `sequence`, `topic_key`

---

### FR-06: Clasificador Automático de Tipo
**Dado** contenido sin tipo explícito
**Cuando** se guarda via `save()`
**Entonces** clasifica por keywords:
| Palabras clave | Tipo |
|---|---|
| error, fail, bug, exception, traceback, fix | `bugfix` |
| decid, elegí, opté, estrategia, tradeoff, arquitectura | `decision` |
| config, configur, yaml, json, env, variable | `config` |
| patrón, pattern, convención, estilo, estándar | `pattern` |
| aprend, learning, descubr, gotcha, truco, tip | `learning` |
| arquitect, infra, deploy, servidor, container, docker | `architecture` |
| (default) | `discovery` |

---

### FR-07: Export Obsidian Live
**Dado** vault Obsidian configurado
**Cuando** `engram obsidian-export --watch --interval 1m`
**Entonces** genera/actualiza:
- `Observations/*.md` con frontmatter: type, project, topic_key, version, tags
- `Sessions/*.md` con timeline
- `Projects/*.md` index
- `Graph/*.md` relaciones (topic_key, supersedes, conflicts_with)
- `Canvas/` mapas de arquitectura

**Criterios:**
- Incremental (solo cambios)
- Frontmatter compatible Dataview
- Graph edges desde `topic_key` y `memory_relations`

---

### FR-08: Recuperación de Contexto (Context Recovery)
**Dado** petición "¿qué pasó en este proyecto?"
**Cuando** se invoca `engram_context(project, days=7)`
**Entonces** retorna JSON estructurado:
```json
{
  "decisions": [...],
  "bugs_fixed": [...],
  "configs_changed": [...],
  "git_activity": "summary",
  "env_changes": [...],
  "processes": [...],
  "llm_summary": "Resumen ejecutivo..."
}
```

---

### FR-09: Systemd Service Unificado
**Dado** instalación en servidor
**Cuando** `systemctl enable --now engram-autocapture@session-<timestamp>`
**Entonces** levanta:
1. MCP server (`engram mcp --tools=agent`)
2. Auto-capture cada 5 min (env, git, processes)
3. Hooks bash via `.bashrc` source
4. Logs a journalctl

---

### NFR (Non-Functional Requirements)

| Requisito | Target |
|---|---|
| Latencia auto-captura | < 100ms |
| Throughput | 100 ops/sec burst |
| Disponibilidad | 99.9% (auto-restart systemd) |
| Persistencia | SQLite + WAL (engram.db) |
| Backup | `engram sync --cloud` diario |
| Privacidad | No captura secrets (filtra *_SECRET, *_KEY, *_TOKEN, PASSWORD*) |
| Trazabilidad | Cada obs tiene `session_id`, `created_at`, `sync_id` |