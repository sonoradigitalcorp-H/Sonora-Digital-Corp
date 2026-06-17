#!/bin/bash
# Update agent context file
set -e

CONTEXT_FILE=".specify/memory/context.md"

cat > "$CONTEXT_FILE" << 'EOF'
# Agent Context

Last updated: $(date)

## Active Specifications

EOF

echo "Agent context updated: ${CONTEXT_FILE}"
