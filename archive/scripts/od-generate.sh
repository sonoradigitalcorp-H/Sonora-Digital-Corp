#!/bin/bash
# Wrapper for Open Design CLI — generates designs from briefs
# Usage: ./od-generate.sh <brief> [design-system] [output-dir]
# Prereq: `pnpm --filter @open-design/daemon build` in ~/open-design/

set -euo pipefail

BRIEF="${1:-}"
DESIGN_SYSTEM="${2:-sonoran-sunset}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
OUTPUT_DIR="${3:-$REPO/webui/static/generated}"
OD_BIN="$HOME/open-design/apps/daemon/bin/od.mjs"

if [ ! -f "$OD_BIN" ]; then
  echo "ERROR: OD daemon not built. Run: cd ~/open-design && pnpm install && pnpm --filter @open-design/daemon build"
  exit 1
fi

mkdir -p "$OUTPUT_DIR"
export PATH="$HOME/open-design/node_modules/.bin:$PATH"
node "$OD_BIN" generate "$BRIEF" --design-system "$DESIGN_SYSTEM" --output "$OUTPUT_DIR"

echo "Generated at: $OUTPUT_DIR"
