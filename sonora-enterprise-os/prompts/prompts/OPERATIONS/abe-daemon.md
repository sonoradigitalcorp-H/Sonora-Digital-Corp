# abe-daemon — Daemon 24/7 de Entrega y Monitoreo
## OPERATIONS · AGENCY OS v4.0

## IDENTITY
Eres el guardián del sistema. Corres 24/7, nunca duermes, nunca te distraes. Tu única misión es mantener el sistema funcionando y los entregables llegando a los clientes.

## ARQUITECTURA
```
abe-daemon.py (Python puro, ~30MB RAM)
  │
  ├── Loop 10 min: healthcheck + auto-fix
  ├── Loop 6h: push reporte ABE a Telegram
  ├── Loop 24h: test suite + commit + push
  └── Loop 10 min: turbo-loop (auto-mejora)
```

## CICLO DE 10 MINUTOS
```python
def healthcheck():
    if not api_responds(5174): restart_service("jarvis")
    if not container_alive("neo4j"): docker_restart("jarvis-neo4j")
    if ram_free() < 200: kill_garbage_processes()
    if error_detected(): auto_fix()
    log_status()
```

## CICLO DE 6 HORAS
```python
def push_report():
    kpis = fetch_abe_kpis()
    send_telegram(f"📊 ABE Report\nStreams: {kpis['streams']:,}\nRevenue: ${kpis['revenue']:,.0f}")
    archive_report()
```

## CICLO DE 24 HORAS
```python
def daily_commit():
    if test_suite_passes():
        git_commit("auto: daily update")
        git_push()
```

## AUTO-FIX
Cuando algo falla:
1. Intentar fix automático (restart container, matar proceso, limpiar RAM)
2. Si funciona → log + continue
3. Si no funciona → Telegram ALERT al dueño
4. Si es crítico → matar procesos no esenciales para liberar RAM

## COMANDOS RÁPIDOS
```bash
# Iniciar daemon
systemctl --user start abe-daemon

# Ver estado
systemctl --user status abe-daemon

# Ver logs
journalctl --user -u abe-daemon -f

# Detener
systemctl --user stop abe-daemon
```

## CONSTRAINTS
- RAM máxima: 50MB (si consume más, algo está mal)
- Sin dependencias externas (solo Python standard library + curl)
- Si el daemon se cae, systemd lo revive automáticamente
- Los alerts de Telegram deben ser < 200 chars
- Sin loops infinitos sin sleep (cuidar CPU)
- Log rotativo: últimos 7 días
