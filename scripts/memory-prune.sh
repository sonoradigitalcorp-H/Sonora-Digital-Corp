#!/bin/bash
# Poda automática de memoria — corre cada domingo 3 AM
# Mantiene Hermes state.db < 100 MB y sincroniza Engram

STATE_DB="$HOME/.hermes/state.db"
ENGRAM_SRC="$HOME/.engram/engram.db"
TWINS="$HOME/.secrets/twins"

echo "[$(date)] === MEMORY PRUNE ==="

# 1. Podar Hermes state — sesiones > 30 días
if [ -f "$STATE_DB" ]; then
  SIZE_BEFORE=$(du -sh "$STATE_DB" | awk '{print $1}')
  
  sqlite3 "$STATE_DB" "
    DELETE FROM messages WHERE session_id NOT IN (
      SELECT id FROM sessions WHERE started_at > strftime('%s', 'now', '-30 days')
    );
    DELETE FROM sessions WHERE started_at < strftime('%s', 'now', '-30 days');
    VACUUM;
  " 2>/dev/null
  
  SIZE_AFTER=$(du -sh "$STATE_DB" | awk '{print $1}')
  echo "Hermes state: $SIZE_BEFORE → $SIZE_AFTER"
fi

# 2. Sincronizar Engram con twins
if [ -f "$ENGRAM_SRC" ]; then
  cp "$ENGRAM_SRC" "$TWINS/mystic/engram.db"
  echo "Engram sincronizado: $(du -sh "$TWINS/mystic/engram.db" | awk '{print $1}')"
fi

# 3. Limpiar backup viejo (solo mantener 1)
rm -f "$HOME/.hermes/state.db.backup.old"
[ -f "$HOME/.hermes/state.db.backup" ] && mv "$HOME/.hermes/state.db.backup" "$HOME/.hermes/state.db.backup.old"

echo "[$(date)] === PRUNE COMPLETE ==="
