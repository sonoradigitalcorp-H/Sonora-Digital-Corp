#!/usr/bin/env bash
set -euo pipefail

# backup.sh — Backup diario del proyecto
#
# Comprime todo el repo con fecha y lo guarda donde digas.
# Uso:
#   bash scripts/backup.sh                    # guarda en ~/sdc-backups/
#   bash scripts/backup.sh /ruta/externa       # guarda en USB/disco externo
#   bash scripts/backup.sh --cron              # modo silencioso para cron

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="${1:-$HOME/sdc-backups}"
MODE="${2:-manual}"

mkdir -p "$BACKUP_DIR/$DATE"

echo "📦 Backup: $DATE"
echo "  Origen: $REPO_ROOT"
echo "  Destino: $BACKUP_DIR/$DATE"

# 1. Backup del repo (con todo el historial git)
git clone --mirror "$REPO_ROOT" "$BACKUP_DIR/$DATE/repo-mirror.git" 2>/dev/null
echo "  ✅ Repo clonado (mirror)"

# 2. Backup de archivos (por si hay algo sin commit)
tar czf "$BACKUP_DIR/$DATE/files.tar.gz" \
  -C "$(dirname "$REPO_ROOT")" \
  "$(basename "$REPO_ROOT")" \
  --exclude=".git" \
  --exclude="node_modules" \
  --exclude="__pycache__" \
  --exclude="*.pyc" \
  2>/dev/null
echo "  ✅ Archivos comprimidos"

# 3. Backup de configs de agentes
for cfg in "$HOME/.config/opencode" "$HOME/.openclaw" "$HOME/.hermes"; do
  if [ -d "$cfg" ]; then
    cname=$(basename "$cfg")
    tar czf "$BACKUP_DIR/$DATE/config-$cname.tar.gz" -C "$(dirname "$cfg")" "$cname" 2>/dev/null
    echo "  ✅ Config $cname"
  fi
done

# 4. Empaquetar todo
cd "$BACKUP_DIR"
tar czf "sdc-full-$DATE.tar.gz" "$DATE"
rm -rf "$DATE"

# 5. Checksum
sha256sum "sdc-full-$DATE.tar.gz" > "sdc-full-$DATE.tar.gz.sha256"
echo "  ✅ Checksum: $(cat sdc-full-$DATE.tar.gz.sha256 | cut -d' ' -f1)"

# 6. Limpiar backups viejos (+30 días)
find "$BACKUP_DIR" -name "sdc-full-*.tar.gz" -mtime +30 -delete 2>/dev/null || true
find "$BACKUP_DIR" -name "sdc-full-*.tar.gz.sha256" -mtime +30 -delete 2>/dev/null || true

# 7. Mostrar último backup
LATEST=$(ls -t "$BACKUP_DIR"/sdc-full-*.tar.gz 2>/dev/null | head -1)
if [ -n "$LATEST" ]; then
  SIZE=$(du -h "$LATEST" | cut -f1)
  echo ""
  echo "📊 Último backup: $(basename "$LATEST") ($SIZE)"
fi

echo ""
echo "✅ Backup completado: $BACKUP_DIR/sdc-full-$DATE.tar.gz"

# Modo cron: no mostrar output si todo sale bien
if [ "$MODE" = "--cron" ]; then
  exec >/dev/null 2>&1
fi
