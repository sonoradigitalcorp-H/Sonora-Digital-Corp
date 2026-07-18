# PLAYBOOK — Brain Sync Recovery

## Arquitectura actual

```
Syncthing local (N45UXVT...) ◄── relay/TLS ──► Syncthing VPS (YMJWVWP...)
Folder: hermes-brain → ~/.hermes/ (Send & Receive)

Local: ~/.hermes/ → /home/mystic/.hermes/
VPS:   ~/.hermes/ → /home/ubuntu/.hermes/

Excluidos (`.stignore`):
  - *.lock, *.pid
  - cache/, audio_cache/, image_cache/, __pycache__/
  - logs/, *.log
  - whatsapp/session/
  - state-snapshots/
  - *.tmp, *.swp, gateway.lock, gateway.pid
  - lsp/node_modules/
  - kanban.db
```

---

## 1. Conflicto de archivos

**Síntoma**: Archivos `.sync-conflict-*` aparecen en `~/.hermes/`.

**Causa**: Mismo archivo editado en ambas máquinas simultáneamente.

**Recovery**:
```bash
# Listar conflictos
find ~/.hermes/ -name "*.sync-conflict-*"
# Revisar diferencias
diff ~/.hermes/config.yaml ~/.hermes/config.yaml.sync-conflict-*
# Decidir cuál versión conservar, borrar el conflicto
rm ~/.hermes/config.yaml.sync-conflict-*
```

**Prevención**: No editar `state.db` en ambas máquinas al mismo tiempo.

---

## 2. state.db corrupto

**Síntoma**: Hermes Agent falla al arrancar, errores de SQLite.

**Causa**: Escritura concurrente o corte durante sync.

**Recovery**:
```bash
# 1. Detener Hermes Agent
ssh ovh "cd ~/hermes-agent && docker compose stop"

# 2. Verificar integridad
sqlite3 ~/.hermes/state.db "PRAGMA integrity_check;"

# 3a. Si está corrupto pero hay backup en Syncthing Trash Can:
ls ~/.config/syncthing/trashcan/  # localizar backup
cp ~/.config/syncthing/trashcan/state.db.* ~/.hermes/state.db

# 3b. O forzar resync completo desde la otra máquina:
rm ~/.hermes/state.db   # local o remoto, según cuál esté corrupto
# Syncthing lo re-descargará automáticamente desde la otra máquina

# 4. Reiniciar Hermes
ssh ovh "cd ~/hermes-agent && docker compose start"
```

**Prevención**: La regla es: Hermes Agent corre SOLO en el VPS. Local solo usa CLI para consultas ligeras. `state.db` nunca se escribe desde local mientras Hermes corre en VPS.

---

## 3. Sync detenido / desconectado

**Síntoma**: Archivos no se replican entre máquinas.

**Causa**: Syncthing caído, firewall, o relay desconectado.

**Recovery**:
```bash
# Local
systemctl --user restart syncthing
systemctl --user status syncthing

# VPS
ssh ovh "sudo systemctl restart syncthing@ubuntu"
ssh ovh "systemctl status syncthing@ubuntu"

# Verificar conexión
curl -s -H "X-API-Key: $(grep -oP '<apikey>\K[^<]+' ~/.config/syncthing/config.xml)" \
  http://127.0.0.1:8384/rest/system/connections | python3 -m json.tool

# Si no se reconecta, verificar puerto 22000 en VPS
ssh ovh "sudo ufw status | grep 22000"
```

**Prevención**: Ambos servicios tienen `Restart=always` en systemd.

---

## 4. Re-par pairing (extremo)

**Síntoma**: Devices muestran "Disconnected" permanente.

**Causa**: Cambio de Device ID (reinstalación), cambio de IP, firewall.

**Recovery**:
```bash
# 1. Obtener Device IDs
syncthing --device-id                                # local
ssh ovh "syncthing --device-id"                      # VPS

# 2. Re-agregar dispositivo (en cada máquina)
syncthing cli config devices add \
  --device-id YMJWVWP-... \
  --name sdc-prod \
  --auto-accept-folders

# 3. Reiniciar ambas
systemctl --user restart syncthing
ssh ovh "sudo systemctl restart syncthing@ubuntu"
```

---

## 5. Rollback completo

Si necesitas deshacer todo el brain sync:

```bash
# 1. Detener Syncthing en ambas
systemctl --user stop syncthing
ssh ovh "sudo systemctl stop syncthing@ubuntu"

# 2. Eliminar carpeta compartida (no borra datos)
syncthing cli config folders add-json '{"id": "hermes-brain", "paused": true}'

# 3. Eliminar .stignore
rm ~/.hermes/.stignore
ssh ovh "rm /home/ubuntu/.hermes/.stignore"

# 4. Desinstalar Syncthing
sudo apt remove -y syncthing
ssh ovh "sudo apt remove -y syncthing"

# 5. Opcional: eliminar config
rm -rf ~/.config/syncthing/
ssh ovh "rm -rf /home/ubuntu/.local/state/syncthing/"
```

---

## 6. Dashboard: lock errors en logs

**Síntoma**: `s6-log: fatal: unable to lock /opt/data/logs/gateways/*/lock: Resource busy`

**Causa**: La carpeta `logs/` en `.stignore` evita el sync, pero los lock files locales del VPS pueden quedar huérfanos.

**Solución**:
```bash
ssh ovh "rm -f /home/ubuntu/.hermes/logs/gateways/*/lock"
ssh ovh "cd ~/hermes-agent && docker compose restart hermes-dashboard"
```
