#!/bin/bash
# Archive legacy repos after confirming sonora-platform works
# Run ONLY after verifying sonora-platform is fully operational

BACKUP_DIR="/home/ubuntu/archive-$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

echo "Archiving legacy projects to $BACKUP_DIR ..."

cat > "$BACKUP_DIR/MANIFEST.md" << EOF
Archive date: $(date)
Source: sonora-platform is the new canonical repo

Archived projects:
- sonora-digital-corp (2.5 GB) - old monorepo (replaced by OpenCode)
- hermes-agent (214 MB) - agent framework (replaced by OpenCode)
- abe-api (372 KB) - API (merged into ABE Service)
- evolution (20 KB) - proposals
- evolucion (280 KB) - dashboards
- abe-business (20 KB) - document
- .openclaw (~50 MB) - gateway (replaced by OpenCode)
- .hermes (~100 MB) - agent config (replaced by OpenCode)

To restore: tar xzf <project>.tar.gz -C /home/ubuntu
To delete originals: rm -rf /home/ubuntu/<project> (only after confirming backup)
EOF

for dir in sonora-digital-corp hermes-agent abe-api evolution evolucion abe-business; do
  if [ -d "/home/ubuntu/$dir" ]; then
    tar czf "$BACKUP_DIR/$dir.tar.gz" -C /home/ubuntu "$dir" 2>/dev/null
    echo "  archived $dir ($(du -sh /home/ubuntu/$dir | cut -f1))"
  fi
done

for dir in .openclaw .hermes; do
  if [ -d "/home/ubuntu/$dir" ]; then
    tar czf "$BACKUP_DIR/$dir.tar.gz" -C /home/ubuntu "$dir" 2>/dev/null
    echo "  archived $dir"
  fi
done

echo "Done. Archives in: $BACKUP_DIR"
echo "Total size: $(du -sh "$BACKUP_DIR" | cut -f1)"
