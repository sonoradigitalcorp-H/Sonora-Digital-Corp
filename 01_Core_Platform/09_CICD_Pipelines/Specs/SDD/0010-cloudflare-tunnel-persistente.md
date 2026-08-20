# SDD 0010: Cloudflare Tunnel Persistente — sonoradigitalcorp.com 24/7 sin VPS

**Estado**: ✅ Implementado y verificado (2026-08-20)
**Autor**: OpenCode COSUDE
**Modelo**: deepseek-v4-flash-free
**Costo**: $0 (solo config local + servicios gratis Cloudflare Free)

## Objetivo

Hacer que el dominio `sonoradigitalcorp.com` responda **24/7 sin depender del VPS OVH** (caído desde 2026-08-19), sirviendo la landing local de la PC del dueño vía Cloudflare Tunnel.

## Contexto

- VPS OVH 149.56.46.173 caído → decidido: página servida desde PC local detrás de router (sin port-forward, sin IP expuesta)
- Dominio registrado en Hostinger, nameservers cambiados a Cloudflare (`gene`/`ian.ns.cloudflare.com`)
- Cloudflare Free: DNS + SSL universal + CDN + Tunnels
- PC local: nginx en :80 sirviendo `/home/mystic/www` + backend node :8000 + gateway hermes :8642

## Arquitectura

```
Visitante ──HTTPS──> Cloudflare Edge (CDN+SSL)
                          │ tunnel QUIC
                     cloudflared (systemd user, PC local)
                          │ http://localhost:80
                       nginx (/home/mystic/www)
```

- **DNS**: `sonoradigitalcorp.com` + `www` → CNAME `a8f01806-a65b-4467-ba7d-ba0360849c54.cfargotunnel.com` (proxied)
- **Tunnel**: named tunnel `sonoradigitalcorp` (ID a8f01806-a65b-4467-ba7d-ba0360849c54)
- **Config**: `~/.cloudflared/config.yml` — ingress: apex + www → `http://localhost:80`, fallback 404

## Componentes

### 1. Certificado de origen (OAuth)
- `~/.cloudflared/cert.pem` — generado con `cloudflared tunnel login`
- Contiene zoneID, accountID y apiToken (usable para API DNS CRUD)

### 2. Tunnel nombrado
```bash
cloudflared tunnel create sonoradigitalcorp
# → a8f01806-a65b-4467-ba7d-ba0360849c54
# credenciales: ~/.cloudflared/a8f01806-...json
```

### 3. DNS en Cloudflare (vía API con token del cert)
```bash
# Borrar A records que bloqueaban:
# 224a56ee... (apex), 705eea60... (www)
# Crear CNAME proxied:
# sonoradigitalcorp.com → <tunnel-id>.cfargotunnel.com
# www → <tunnel-id>.cfargotunnel.com
```

### 4. Servicio systemd user
**Path**: `~/.config/systemd/user/cloudflared-tunnel.service`

```ini
[Unit]
Description=Cloudflare Tunnel sonoradigitalcorp
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/local/bin/cloudflared tunnel run a8f01806-a65b-4467-ba7d-ba0360849c54
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
```

**Activación**:
```bash
systemctl --user daemon-reload
systemctl --user enable cloudflared-tunnel.service   # auto-start boot
systemctl --user start cloudflared-tunnel.service    # por separado (evita hang)
```

**Requisito persistencia**: `loginctl enable-linger mystic` (ya activo)

## Criterios de aceptación

- [x] `systemctl --user status cloudflared-tunnel.service` → **active (running)**, enabled
- [x] `curl -sI https://sonoradigitalcorp.com` → **HTTP/2 200** (server: cloudflare)
- [x] `curl -sI https://www.sonoradigitalcorp.com` → **HTTP/2 200**
- [x] Sobrevive restart del servicio (Restart=on-failure)
- [ ] Sobrevive reboot de la PC (validar en próximo reinicio)

## Errores conocidos y soluciones

| Síntoma | Causa | Fix |
|---|---|---|
| Error 1033 (Cloudflare no puede resolver túnel) | tunnel no corriendo | `systemctl --user start cloudflared-tunnel.service` |
| HTTP 530 | origen caído (nginx/cloudflared) | verificar servicio + `nginx -t` |
| `cloudflared tunnel run` rechaza `--config`/`--no-autoupdate` | solo acepta 1 argumento (ID) | `cloudflared tunnel run <ID>` a secas; config.yml se lee de ~/.cloudflared |
| `systemctl --user enable --now` cuelga el shell | timeout del wrapper | hacer `enable` y `start` por separado |
| Login OAuth expira ~90s | URL de un solo uso | lanzar con `nohup cloudflared tunnel login &` y autorizar en nueva pestaña |

## Riesgos

- **PC apagada/sin internet** = página caída (aceptado: sin VPS, la página vive en la PC del dueño). Mitigación futura: worker estático de respaldo en Cloudflare Pages.
- Auto-update de cloudflared podría romper → monitorear `journalctl --user -u cloudflared-tunnel`
- RAM: 59MB del proceso — aceptable en PC 3.3GB (regla de oro respetada: proceso ligero)

## Referencias

- Video aprendizaje Cloudflare+IA: `01_Core_Platform/05_SelfImprovement/learning/youtube/qT784npVXF4_cloudflare_ia_transcript.txt`
- Skill tema: `~/.hermes/skills/sdc/cloudflare-ia-internet/SKILL.md`
