#!/bin/bash
# auto-doc.sh — Wrapper para auto-doc.py
# Uso: ./scripts/auto-doc.sh [--auto | --spec-id ... --title ...]

set -e
DIR="$(cd "$(dirname "$0")/.." && pwd)"

if [ "$1" = "--auto" ]; then
    echo "=== Auto-Doc: Parsing AGENTS.md ==="
    python3 "$DIR/scripts/auto-doc.py" --auto
elif [ $# -gt 0 ]; then
    echo "=== Auto-Doc: Generating from args ==="
    python3 "$DIR/scripts/auto-doc.py" "$@"
else
    echo "Uso:"
    echo "  $0 --auto                                   # Auto desde AGENTS.md"
    echo "  $0 --spec-id SPEC-20260703-003 --title '...' # Manual"
    echo ""
    echo "Modo interactivo:"
    python3 "$DIR/scripts/auto-doc.py" --auto 2>/dev/null || true
    echo ""
    echo "O ejecuta: python3 scripts/auto-doc.py -h"
    exit 1
fi
