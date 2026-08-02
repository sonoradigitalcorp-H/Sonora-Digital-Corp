#!/bin/bash
# Frontend: Generate React/Vue/Svelte component
set -e

NAME="${1:-}"
FRAMEWORK="${2:-react}"
TYPE="${3:-ui}"  # ui, form, data, layout, feedback
if [ -z "$NAME" ]; then
  echo "Usage: $0 <name> [framework] [type]"
  echo "Types: ui, form, data, layout, feedback"
  exit 1
fi

COMPONENT_DIR="sonora-digital-corp/apps/frontends/app/src/components"
mkdir -p "$COMPONENT_DIR/$TYPE"

FILE="$COMPONENT_DIR/$TYPE/${NAME}.tsx"

cat > "$FILE" << EOF
import React from 'react'
import { cn } from '@/lib/utils'

interface ${NAME}Props {
  className?: string
  children?: React.ReactNode
}

export function ${NAME}({ className, children, ...props }: ${NAME}Props) {
  return (
    <div className={cn('${NAME.toLowerCase()}', className)} {...props}>
      {children}
    </div>
  )
}

${NAME}.displayName = '${NAME}'
export default ${NAME}
EOF

# Create index export
INDEX_FILE="$COMPONENT_DIR/$TYPE/index.ts"
if [ ! -f "$INDEX_FILE" ] || ! grep -q "export.*${NAME}" "$INDEX_FILE"; then
  echo "export { ${NAME} } from './${NAME}'" >> "$INDEX_FILE"
fi

echo "Component created: $FILE"
echo "Exported from: $INDEX_FILE"