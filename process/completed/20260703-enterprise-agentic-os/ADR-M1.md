# ADR — Truth Guardian: Systemd-based Drift Scanner & Health Checker

| Campo | Valor |
|-------|-------|
| **ID** | ADR-M1-001 |
| **Fecha** | 2026-07-03 |
| **Estado** | aceptado |

## Contexto

Necesitamos un servicio 24/7 que verifique que TRUTH.md coincide con la realidad del VPS, monitoree la salud de todos los servicios, ejecute compliance auditor, y envíe alertas por Telegram. Las opciones consideradas: Docker container, systemd service, script cron con systemd timer.

## Decisión

**Systemd service** (no Docker). Razones:
1. Truth Guardian necesita leer `ss -tlnp`, `docker ps`, y archivos del sistema host — desde Docker requeriría montar `/proc` y `/var/run/docker.sock`, que es inseguro y complejo
2. Systemd permite reinicio automático con `Restart=always`, bajo overhead (~20MB RAM)
3. Un solo binary Python es más simple de debuggear que un container
4. CRON + systemd timer también se consideró pero se descartó porque la frecuencia mínima es 1min, no permite health check continuo ni WebSocket

## Consecuencias

- Positivas: Acceso directo a sistema de archivos host, sin dependencia de Docker, fácil debug
- Negativas: No portátil a otros servidores que no usen systemd, requiere Python en el host
- Mitigación: Si se necesita portabilidad en el futuro, encapsular la lógica en Docker con volúmenes bind

## Alternativas

| Alternativa | Pros | Contras |
|-------------|------|---------|
| Docker container | Portátil, aislado | Requiere montar /proc, /var/run/docker.sock, inseguro |
| Cron + systemd timer | Simple, sin proceso residente | No permite health check continuo, polling máximo 1min |
