#!/bin/bash
# Frontend: Create component/page
set -e

TYPE="${1:-component}"
NAME="${2:-}"
FRAMEWORK="${3:-react}"
if [ -z "$NAME" ]; then
  echo "Usage: $0 <type> <name> [framework]"
  echo "Types: component, page, hook, context, layout"
  echo "Frameworks: react, vue, svelte, solid"
  exit 1
fi

FRONTEND_DIR="sonora-digital-corp/apps/frontends/app/src"
mkdir -p "$FRONTEND_DIR/components" "$FRONTEND_DIR/pages" "$FRONTEND_DIR/hooks" "$FRONTEND_DIR/context" "$FRONTEND_DIR/layouts"

case $TYPE in
  component)
    DIR="$FRONTEND_DIR/components"
    ;;
  page)
    DIR="$FRONTEND_DIR/pages"
    ;;
  hook)
    DIR="$FRONTEND_DIR/hooks"
    ;;
  context)
    DIR="$FRONTEND_DIR/context"
    ;;
  layout)
    DIR="$FRONTEND_DIR/layouts"
    ;;
  *)
    echo "Unknown type: $TYPE"
    exit 1
    ;;
esac

case $FRAMEWORK in
  react)
    EXT="tsx"
    ;;
  vue)
    EXT="vue"
    ;;
  svelte)
    EXT="svelte"
    ;;
  solid)
    EXT="tsx"
    ;;
  *)
    echo "Unknown framework: $FRAMEWORK"
    exit 1
    ;;
esac

FILE="$DIR/${NAME}.$EXT"

# Generate based on type and framework
if [ "$FRAMEWORK" = "react" ] || [ "$FRAMEWORK" = "solid" ]; then
  cat > "$FILE" << EOF
import React from 'react'

interface ${NAME}Props {
  // Add props here
}

export function ${NAME}({ }: ${NAME}Props) {
  return (
    <div className="${NAME.toLowerCase()}">
      {/* ${NAME} component */}
    </div>
  )
}

export default ${NAME}
EOF
elif [ "$FRAMEWORK" = "vue" ]; then
  cat > "$FILE" << EOF
<script setup lang="ts">
interface Props {
  // Add props here
}

const props = withDefaults(defineProps<Props>(), {
  // Default props
})
</script>

<template>
  <div class="${NAME.toLowerCase()}">
    <!-- ${NAME} component -->
  </div>
</template>

<style scoped>
.${NAME.toLowerCase()} {
  /* styles */
}
</style>
EOF
elif [ "$FRAMEWORK" = "svelte" ]; then
  cat > "$FILE" << EOF
<script lang="ts">
  export interface Props {
    // Add props here
  }
  
  let { }: Props = $props()
</script>

<div class="${NAME.toLowerCase()}">
  <!-- ${NAME} component -->
</div>

<style>
  .${NAME.toLowerCase()} {
    /* styles */
  }
</style>
EOF
fi

echo "Created: $FILE"