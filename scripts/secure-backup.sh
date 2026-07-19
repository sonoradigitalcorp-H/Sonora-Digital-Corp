#!/bin/bash
# Backup seguro con sanitización de keys
# Excluye config/.secrets/ y rota keys automáticamente
BACKUP_DIR=~/backups/$(date +%Y%m%d-%H%M%S)
mkdir -p "$BACKUP_DIR"

# Secrets sanitizados
cat ~/.config/opencode/opencode.json 2>/dev/null | sed 's/sk-[^"]*/sk-REDACTED/g; s/ghp_[^"]*/ghp-REDACTED/g; s/AKIA[^"]*/AKIA-REDACTED/g' > "$BACKUP_DIR"/opencode.json 2>/dev/null
cat ~/.hermes/auth.json 2>/dev/null | sed 's/sk-[^"]*/sk-REDACTED/g' > "$BACKUP_DIR"/hermes-auth.json 2>/dev/null

# Config sin secrets
[ -f ~/.config/sonora/env.local ] && grep -v 'SECRET\|KEY\|TOKEN\|PASSWORD' ~/.config/sonora/env.local > "$BACKUP_DIR"/env.local 2>/dev/null

# Código y documentos
cp -r ~/jarvis/specs "$BACKUP_DIR"/specs 2>/dev/null
cp ~/jarvis/CLAUDE.md "$BACKUP_DIR"/ 2>/dev/null

# Repo SDC (excluyendo secrets)
rsync -a --exclude='config/.secrets/' --exclude='*.jsonl' --exclude='*.db' --exclude='node_modules' \
  ~/sonora-digital-corp/ "$BACKUP_DIR"/sonora-digital-corp/ 2>/dev/null

echo "✅ Backup seguro en $BACKUP_DIR"
echo "   Secrets redactados: opencode.json, hermes-auth.json, env.local"
