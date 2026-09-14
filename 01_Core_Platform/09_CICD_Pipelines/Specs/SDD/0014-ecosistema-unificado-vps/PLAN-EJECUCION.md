# Plan de Ejecución — SDD 0014

**Ejecutar en orden. Cada fase requiere aprobación del Jefe antes de continuar.**

## Criterios de Aceptación (Definition of Done)
- [ ] Gateway local (mysticpc) apagado, puerto 8642 libre
- [ ] VPS 45.90.108.12 = única fuente canónica (health 200)
- [ ] 3 bots Telegram activos en VPS: hermosillo-cont, sonora-digital-corp, tu-bandera
- [ ] Token tu-bandera sin errores 401/getMe fallido
- [ ] Memoria consolidada: memory_store.db VPS tiene ≥5 facts, Engram tiene ≥808 obs
- [ ] Qdrant VPS tiene 3 colecciones: engram_memories, hermes, tubandera_kb
- [ ] Ollama VPS tiene ≥2 modelos: nomic-embed-text + LLM (qwen/gemma)
- [ ] opencode.db backup creado, limpieza documentada para ejecutar cuando opencode no esté corriendo
- [ ] ESTADO.md actualizado con estado final
- [ ] Git commit exitoso sin errores SPECJUDGE

## Pre-flight Checklist (ANTES de empezar)
- [ ] Backup de `~/.hermes/memory_store.db` local
- [ ] Backup de `~/.engram/engram.db` local
- [ ] Backup de `~/.local/share/opencode/opencode.db` local
- [ ] Verificar SSH `root@45.90.108.12` funciona
- [ ] Verificar `docker ps sdc-hermes` = Up healthy en VPS
- [ ] Token tu-bandera nuevo listo (guardar en `.env` como `TU_BANDERA_TOKEN`)

## Fase 1: VPS como Fuente Canónica (30 min)
1. SSH al VPS, verificar `curl http://127.0.0.1:8642/health` = 200
2. Verificar bots Telegram: `config.yaml` → hermosillo-cont + sonora-digital-corp enabled
3. **Local**: `systemctl --user stop hermes-gateway`
4. Verificar `ss -tlnp | grep 8642` local = vacío
5. Verificar `ps aux | grep hermes` local = 0 procesos gateway
6. **Checkpoint**: Aprobar antes de Fase 2

## Fase 2: Token Tu-Bandera (15 min)
1. SSH VPS: crear `/opt/sdc/hermes-data/.env` con `TU_BANDERA_TOKEN=<token>`
2. `chmod 600 /opt/sdc/hermes-data/.env`
3. Editar `config.yaml` VPS: cambiar token hardcodeado → `${TU_BANDERA_TOKEN}`
4. `docker compose restart sdc-hermes`
5. Verificar Telegram getMe para tu-bandera: bot activo
6. Verificar no hay doble polling
7. **Checkpoint**: Aprobar antes de Fase 3

## Fase 3: Fusión de Memorias (45 min)
1. SSH VPS: crear `/tmp/hermes_backup_YYYYMMDD/`
2. Copiar desde local: `scp ~/.engram/engram.db root@VPS:/tmp/hermes_backup/`
3. Copiar desde local: `scp ~/.hermes/memory_store.db root@VPS:/tmp/hermes_backup/`
4. Copiar desde VPS: `scp root@VPS:/opt/sdc/hermes-data/memory_store.db /tmp/hermes_backup/`
5. Verificar backups (tamaño, `sqlite3 pragma integrity_check`)
6. **Migrar facts**: insertar desde ambas memory_store.db a Engram
7. Copiar `engram.db` consolidado al VPS: `scp ~/.engram/engram.db root@VPS:/opt/sdc/hermes-data/`
8. Configurar Hermes VPS para usar Engram: `memory_enabled: true`
9. Crear colecciones Qdrant: `engram_memories`, `hermes`
10. Verificar `curl localhost:6333/collections` → 2+ colecciones con puntos
11. Test factual: preguntar algo que esté en la memoria consolidada
12. **Checkpoint**: Aprobar antes de Fase 4

## Fase 4: Limpieza opencode.db (20 min)
1. Backup: `cp ~/.local/share/opencode/opencode.db /tmp/opencode_backup_YYYYMMDD/`
2. Verificar backup: `sqlite3 <backup> "pragma integrity_check;"` = ok
3. Conectar a la DB: `sqlite3 ~/.local/share/opencode/opencode.db`
4. Identificar sesiones recientes (últimos 30 días): `select id, time_created from session order by time_created desc;`
5. Borrar eventos viejos de sesiones eliminadas
6. Borrar parts/messages de sesiones eliminadas
7. `VACUUM;`
8. Verificar: `ls -lh opencode.db` <= 300 MB
9. Verificar: `pragma integrity_check` = ok
10. Abrir opencode y verificar que funciona
11. **Checkpoint**: Verificar que opencode responde correctamente

## Fase 5: Estabilidad (opcional, solo si se mantiene gateway local)
1. Verificar RAM disponible post-cambios
2. Configurar `Restart=on-failure` en systemd
3. Monitorear 1h: logs sin WARNING
4. Verificar MCP hermes-agents conecta
5. **Checkpoint**: Final

## Post-Flight
- [ ] Git commit de todos los cambios de config/docs
- [ ] Actualizar `ESTADO.md` con el nuevo estado
- [ ] Guardar en Engram: decisión de consolidación VPS
- [ ] Verificar web pública: sonoradigitalcorp.com = 200, tubandera.online = 200
- [ ] Enviar resumen al Jefe por WhatsApp
