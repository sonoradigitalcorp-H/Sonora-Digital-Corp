# Manual de Administración del VPS

## Contexto
VPS en OVH (149.56.46.173) con Ubuntu 26.04. Alberga todos los servicios de Sonora Digital Corp.

## Conexión
```bash
ssh ubuntu@149.56.46.173
# Con forwarding (recomendado para laptop):
ssh -L 8080:localhost:8080 -L 5180:localhost:5180 -L 5174:localhost:5174 ubuntu@149.56.46.173
```

## Servicios core (systemd --user)
| Servicio | Comando |
|----------|---------|
| Web UI | `systemctl --user restart jarvis-webui` |
| ABE Service | `systemctl --user restart abe-service` |
| Hermes MCP | `systemctl --user restart hermes-gateway` |
| Evolution Dashboard | `systemctl --user restart evolucion-dashboard` |

## Servicios Docker
```bash
docker compose -f infra/docker-compose.yml ps
docker compose -f infra/docker-compose.products.yml ps
```

## Logs
```bash
journalctl --user -u abe-service -n 50 --no-pager
docker logs content-server --tail 50
```

## Backup
Cron diario 3 AM en `/home/ubuntu/backups/`.
Manual: `bash scripts/close-session.sh` (commitea todo antes).

## Troubleshooting
- **Servicio caído**: `systemctl --user restart <servicio>`
- **Docker caído**: `docker compose -f infra/docker-compose.yml restart <servicio>`
- **Disco lleno**: `df -h` → `docker system prune -af`
- **Sin internet**: `ping 8.8.8.8` → `sudo systemctl restart networking`
