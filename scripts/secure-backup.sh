#!/bin/bash
# Backup seguro con sanitización de keys
BACKUP_DIR=~/backups/$(date +%Y%m%d-%H%M%S)
mkdir -p "$BACKUP_DIR"

cat ~/.config/opencode/opencode.json | sed 's/sk-[^"]*/sk-REDACTED/g' > "$BACKUP_DIR"/opencode.json 2>/dev/null
cat ~/.hermes/auth.json | sed 's/sk-[^"]*/sk-REDACTED/g' > "$BACKUP_DIR"/hermes-auth.json 2>/dev/null
cp ~/.config/sonora/env.local "$BACKUP_DIR"/env.local 2>/dev/null
cp -r ~/jarvis/specs "$BACKUP_DIR"/specs 2>/dev/null
cp ~/jarvis/CLAUDE.md "$BACKUP_DIR"/ 2>/dev/null
cp ~/jarvis/docs/TROUBLESHOOTING.md "$BACKUP_DIR"/ 2>/dev/null

echo "✅ Backup seguro en $BACKUP_DIR"
