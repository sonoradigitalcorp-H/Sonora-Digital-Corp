#!/bin/bash
# Install pipeline git hooks
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOKS_DIR="$BASE_DIR/.git/hooks"

for hook in pre-commit post-commit; do
  src="$BASE_DIR/.github/hooks/$hook"
  dest="$HOOKS_DIR/$hook"
  if [ -f "$src" ]; then
    cp "$src" "$dest"
    chmod +x "$dest"
    echo "Installed: $dest"
  fi
done

echo "✓ Git hooks installed"
