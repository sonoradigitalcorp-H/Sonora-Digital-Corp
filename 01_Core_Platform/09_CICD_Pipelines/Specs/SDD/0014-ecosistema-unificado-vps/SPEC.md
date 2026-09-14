# Spec SDD 0014 — Consolidación del Ecosistema: VPS como Fuente Canónica

**ID**: 0014-ecosistema-unificado-vps
**Version**: 1.0.0
**Date**: 2026-09-14
**Author**: MYSTIC / SDC
**Status**: DRAFT

## Resumen

Consolidar TODO el ecosistema Hermes (memoria, orquestación, tokens, sesiones) en el
VPS Hostinger `45.90.108.12` como **fuente canónica única**. La laptop pasa a ser
solo terminal de edición (editor + opencode). Eliminar fragmentación de memoria,
duplicidad de gateways, y DBs infladas.

## Problema Actual (Diagnóstico 2026-09-14)

### 1. Dos Hermes vivos, desconectados
- **Local** (mysticpc): gateway `127.0.0.1:8642` (pid 823, arrancó 16:42). Responde a este chat.
- **VPS** (45.90.108.12): `sdc-hermes` contenedor, Up 2d healthy. Gateway FATAL:
  `telegram_polling_conflict` + token tu-bandera revocado.

### 2. Memoria fragmentada en 3 bases sin sincronizar
| Ubicación | Tipo | Contenido |
|-----------|------|-----------|
| `~/.engram/engram.db` (local) | SQLite | 801 observaciones, 477 sesiones, 1162 prompts |
| `~/.hermes/memory_store.db` (local) | SQLite | 4 facts |
| `/opt/sdc/hermes-data/memory_store.db` (VPS) | SQLite | 5 facts |
| Qdrant VPS `:6333` | Vector | Solo `tubandera_kb` (0 puntos) |
| Qdrant local `:6333` | — | **NO CORRE** (000) |

### 3. DB opencode inflada
- `opencode.db` = **2.2 GB** (177 sesiones, 23,930 msgs, 98,814 parts, 345K events)
- Tabla `event` = **1.68 GB** (snapshots `message.updated.1` repetidos)
- WAL = 4 MB. SQLite integrity OK.

### 4. Tokens y polling
- Tu-bandera token caducado en VPS: `TU_BANDERA_TOKEN` en `.env` (antiguo, revocado)
- Token nuevo provisto por Jefe: guardar en `.env` como `TU_BANDERA_TOKEN` (chmod 600)
- Telegram polling conflict (doble instancia compitiendo por getUpdates)

### 5. Estabilidad gateway local
- Gateway crash exit_nonzero: 11-sep x4, 12-sep x1 (logs gateway-exit-diag)
- RAM laptop 3.3GB, disponible 122MB → gateway muere por memoria
- MCP `hermes-agents` fallando cada 5 min (parked, Connection closed)

## Constitution Check

### Principio I: Orquestación Única
- [ ] **Una sola instancia de Hermes corriendo** (VPS, no local)
- [ ] **Gateway local apagado** después de migrar
- [ ] **Telegram bots operando SOLO desde VPS** (sin doble polling)

### Principio II: Separación Determinista vs LLM
- [ ] **Memoria Engram = fuente única** de observaciones (no memory_store fragmentadas)
- [ ] **Qdrant VPS** como vector store central (colecciones por proyecto)
- [ ] **Embeddings** corriendo en VPS (nomic-embed-text vía Ollama)

### Principio III: Cargas pesadas SOLO en VPS
- [ ] **Hermes gateway** en VPS como único orquestador
- [ ] **Engram serve** corriendo en VPS (puerto 7437)
- [ ] **Ollama VPS** con modelos necesarios (nomic-embed-text, qwen3:4b)
- [ ] Laptop: solo editor + terminal, cero procesos pesados

### Principio IV: Testing
- [ ] **Verificación SSH** de cada paso del plan
- [ ] **Health checks** antes/después de cada cambio
- [ ] **Rollback** documentado para cada fase

### Principio V: Trazabilidad
- [ ] **Cada cambio** registrado en commit + ESTADO.md
- [ ] **Secretos** siempre en `.env` (chmod 600), nunca hardcodeados
- [ ] **Git** como fuente de verdad del código (no de los datos)

## Alcance del Proceso

### Fase 1: VPS como Fuente Canónica
**Objetivo**: Apagar el Hermes local duplicado, confirmar VPS como único orquestador.

**Pasos**:
1. Verificar que `sdc-hermes` VPS está healthy y responde `/health`
2. Confirmar que Telegram bots en VPS están configurados (sonora-digital-corp, hermosillo-cont, tu-bandera)
3. **Apagar gateway local** (`systemctl --user stop hermes-gateway`)
4. Verificar que no hay procesos Hermes locales (`ps aux | grep hermes`)
5. Confirmar que la laptop SOLO tiene: editor, terminal, opencode, gemini CLI

**Criterios de aceptación**:
- AC-01: `ss -tlnp | grep 8642` en VPS = LISTEN (gateway activo)
- AC-02: `ss -tlnp | grep 8642` en local = VACÍO (gateway apagado)
- AC-03: `docker ps sdc-hermes` = Up healthy
- AC-04: `curl http://127.0.0.1:8642/health` en VPS = 200

### Fase 2: Token Tu-Bandera + Polling Fix
**Objetivo**: Token nuevo aplicado, polling sin conflicto.

**Pasos**:
1. Guardar token nuevo en `/opt/sdc/hermes-data/.env` como `TU_BANDERA_TOKEN` (chmod 600)
2. Actualizar `config.yaml` VPS para referenciar `${TU_BANDERA_TOKEN}` (NO hardcodear)
3. Verificar que solo UNA instancia polling el token (VPS, no local)
4. Verificar `tubandera-bot.service` en VPS (si existe) o integrar al sdc-hermes
5. Test: `curl` al endpoint del bot tu-bandera desde VPS → 200 OK

**Criterios de aceptación**:
- AC-05: Token en `.env` = `TU_BANDERA_TOKEN=<valor_provisto>` (chmod 600)
- AC-06: `grep -r "TU_BANDERA_TOKEN" /opt/sdc/hermes-data/config.yaml` = referencia `${TU_BANDERA_TOKEN}`
- AC-07: Telegram getWebhookInfo o getMe para tu-bandera → bot activo sin error
- AC-08: No hay doble polling (un solo PID de Telegram por bot)

### Fase 3: Fusión de Memorias
**Objetivo**: Una sola base de memoria (Engram) como fuente canónica.

**Pasos**:
1. **Backup** de ambas `memory_store.db` (local + VPS) y `engram.db` (local)
2. **Extraer** facts de `memory_store.db` local (4 facts) y VPS (5 facts)
3. **Migrar** facts a Engram (via `engram save` o insert directo)
4. **Copiar** `engram.db` local → VPS (`/opt/sdc/hermes-data/engram.db`)
5. **Configurar** Hermes VPS para usar Engram como memoria (no memory_store)
6. **Activar** `memory_enabled: true` en config Hermes VPS
7. **Crear** colecciones Qdrant faltantes en VPS (engram_memories, hermes)
8. **Verificar** que Qdrant VPS tiene las colecciones con puntos

**Criterios de aceptación**:
- AC-09: Backup de ambas DBs existe en `/tmp/hermes_backup_YYYYMMDD/`
- AC-10: `engram stats` en VPS muestra observations >= 810 (801 local + 5 VPS + nuevos)
- AC-11: Qdrant VPS tiene colección `engram_memories` con puntos > 0
- AC-12: `memory_enabled: true` en config Hermes VPS
- AC-13: Hermes VPS responde preguntas que requieren memoria (test factual)

### Fase 4: Limpieza opencode.db
**Objetivo**: Reducir 2.2GB → ~200MB sin perder datos críticos.

**Pasos**:
1. **Backup** de `opencode.db` completo
2. **Identificar** sesiones a conservar (últimas 30 días o N más recientes)
3. **Borrar** eventos `message.updated` de sesiones anteriores a fecha corte
4. **Borrar** parts de sesiones eliminadas
5. **Borrar** messages de sesiones eliminadas
6. **Borrar** sesiones huérfanas
7. **VACUUM** la DB
8. **Verificar** integrity check OK
9. **Verificar** que opencode abre correctamente con la DB reducida

**Criterios de aceptación**:
- AC-14: Backup existe en `/tmp/opencode_backup_YYYYMMDD/`
- AC-15: `ls -lh opencode.db` post-limpieza <= 300 MB
- AC-16: `sqlite3 opencode.db "pragma integrity_check;"` = ok
- AC-17: `sqlite3 opencode.db "select count(*) from session;"` >= 10 (sesiones recientes conservadas)
- AC-18: opencode abre y responde correctamente post-limpieza

### Fase 5: Estabilidad Gateway Local (si se mantiene)
**Objetivo**: Si el gateway local se mantiene como fallback, que sea estable.

**Pasos** (SOLO si se decide mantener local):
1. **Limitar** RAM del gateway (ulimit o cgroup)
2. **Configurar** restart policy (systemd Restart=on-failure, StartLimitBurst=3)
3. **Monitorear** MCP hermes-agents (verificar por qué falla cada 5 min)
4. **Configurar** NotifierNous (auth pendiente)

**Criterios de aceptación**:
- AC-19: Gateway local no muere por RAM en 24h de uso continuo
- AC-20: MCP hermes-agents conecta sin errores por 1h
- AC-21: Logs sin WARNING de memory/parking por 1h

## Arquitectura Objetivo (post-fase 3)

```
┌─────────────────────────────────────────────────────┐
│                  LAPTOP (mysticpc)                   │
│  Editor (opencode/gemini) → terminal → nothing else │
│  RAM libre: 3.3GB - hermes = ~3GB                   │
└───────────────────────┬─────────────────────────────┘
                        │ SSH tunnel / API
                        ▼
┌─────────────────────────────────────────────────────┐
│              VPS HOSTINGER 45.90.108.12             │
│                                                     │
│  ┌─────────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ sdc-hermes  │  │ Engram   │  │ Qdrant        │  │
│  │ :8642       │  │ :7437    │  │ :6333         │  │
│  │ (gateway)   │  │ (memoria)│  │ (vectors)     │  │
│  └──────┬──────┘  └──────────┘  └───────────────┘  │
│         │                                            │
│  ┌──────┴──────┐  ┌──────────┐  ┌───────────────┐  │
│  │ Telegram    │  │ Ollama   │  │ Supabase      │  │
│  │ bots (3)    │  │ :11434   │  │ :5432         │  │
│  │ polling     │  │ nomic    │  │ PostgreSQL    │  │
│  └─────────────┘  └──────────┘  └───────────────┘  │
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐     │
│  │ nginx    │  │ n8n      │  │ Grafana       │     │
│  │ 80/443   │  │ :5678    │  │ :3000         │     │
│  └──────────┘  └──────────┘  └───────────────┘     │
└─────────────────────────────────────────────────────┘
```

## Seguridad

- **Tokens**: SIEMPRE en `.env` (chmod 600), referenciados como `${VAR}` en config
- **SSH**: Llave ed25519, sin password, root only
- **Firewall**: UFW 22/80/443, todo lo demás en loopback
- **Secretos**: NUNCA en git, NUNCA en config versionable
- **Backup**: Antes de cada fase, backup en `/tmp/` con timestamp

## Rollback por Fase

| Fase | Rollback |
|------|----------|
| 1 (VPS canonical) | `systemctl --user start hermes-gateway` en local |
| 2 (Token) | Restaurar `.env` anterior + restart sdc-hermes |
| 3 (Memoria) | Restaurar backups de memory_store.db y engram.db |
| 4 (opencode.db) | Restaurar desde `/tmp/opencode_backup_*` |
| 5 (Estabilidad) | Revertir config systemd + restart |

## Criterios de Aceptación Globales

| ID | Criterio | Verificación |
|----|----------|--------------|
| G-01 | **Un solo Hermes activo** (VPS) | `ps aux | grep hermes` en local = 0 procesos gateway |
| G-02 | **Memoria única** (Engram en VPS) | `engram stats` VPS = observations >= 810 |
| G-03 | **Qdrant funcional** en VPS | `curl localhost:6333/collections` = 2+ colecciones con puntos |
| G-04 | **Token tu-bandera activo** | Telegram bot tu-bandera responde getMe |
| G-05 | **opencode.db reducida** | `ls -lh opencode.db` <= 300 MB |
| G-06 | **Web pública OK** | `curl sonoradigitalcorp.com` = 200 |
| G-07 | **Web tubandera OK** | `curl tubandera.online` = 200 |
| G-08 | **Gateway VPS estable** | No crashes en 24h (logs sin exit_nonzero) |
| G-09 | **Secretos seguros** | Cero tokens en git, todos en .env chmod 600 |
| G-10 | **Rollback probado** | Cada fase tiene backup verificado antes de ejecutar |

## Dependencias

- SSH root@45.90.108.12 con llave `~/.ssh/id_ed25519`
- Token tu-bandera nuevo (provisto por usuario)
- Docker Compose en VPS (`/opt/sdc/docker-compose.yml`)
- edge-tts local (para pruebas de voz, no crítico)
- Engram v1.19.0 binario (ya instalado local)

## Fuente de Verdad

| Dato | Fuente post-migración |
|------|----------------------|
| Código | GitHub `next` branch |
| Memoria | Engram en VPS (`/opt/sdc/hermes-data/engram.db`) |
| Config | `/opt/sdc/hermes-data/config.yaml` + `.env` |
| Secrets | `/opt/sdc/hermes-data/.env` (chmod 600) |
| Vector store | Qdrant VPS `:6333` |
| Datos | Supabase VPS `:5432` |
| Web | nginx VPS `:80/:443` |

## Notas de Implementación

- **NO tocar** el código de la laptop durante la migración (solo operaciones en VPS)
- **Cada fase** se verifica ANTES de pasar a la siguiente
- **El usuario aprueba** cada fase antes de continuar
- **Si algo falla**, se ejecuta rollback inmediato
- **Git commit** después de cada fase exitosa (cambios en config/docs, no secrets)
