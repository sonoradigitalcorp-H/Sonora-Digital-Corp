#!/bin/bash
# Web: Create new web application
set -e

APP_NAME="${1:-}"
FRAMEWORK="${2:-nextjs}"
if [ -z "$APP_NAME" ]; then
  echo "Usage: $0 <app-name> [framework]"
  echo "Frameworks: nextjs, astro, vite-react, vite-vue, sveltekit"
  exit 1
fi

APP_DIR="sonora-digital-corp/apps/frontends/$APP_NAME"
mkdir -p "$APP_DIR"

echo "Creating $FRAMEWORK web app: $APP_NAME"

case $FRAMEWORK in
  nextjs)
    cat > "$APP_DIR/package.json" << EOF
{
  "name": "$APP_NAME",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "14.x",
    "react": "^18",
    "react-dom": "^18"
  },
  "devDependencies": {
    "@types/node": "^20",
    "@types/react": "^18",
    "@types/react-dom": "^18",
    "typescript": "^5",
    "eslint": "^8",
    "eslint-config-next": "14.x"
  }
}
EOF
    mkdir -p "$APP_DIR/src/app"
    cat > "$APP_DIR/src/app/page.tsx" << EOF
export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold">$APP_NAME</h1>
      <p className="mt-4 text-lg">Welcome to your new Next.js app</p>
    </main>
  )
}
EOF
    cat > "$APP_DIR/tsconfig.json" << EOF
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": { "@/*": ["./src/*"] }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
EOF
    ;;
  astro)
    cat > "$APP_DIR/package.json" << EOF
{
  "name": "$APP_NAME",
  "type": "module",
  "version": "0.0.1",
  "scripts": {
    "dev": "astro dev",
    "build": "astro build",
    "preview": "astro preview"
  },
  "dependencies": {
    "astro": "^4.x"
  }
}
EOF
    mkdir -p "$APP_DIR/src/pages"
    cat > "$APP_DIR/src/pages/index.astro" << EOF
---
---
<html lang="en">
  <head><title>$APP_NAME</title></head>
  <body>
    <main class="min-h-screen flex flex-col items-center justify-center p-24">
      <h1 class="text-4xl font-bold">$APP_NAME</h1>
      <p class="mt-4 text-lg">Welcome to your new Astro app</p>
    </main>
  </body>
</html>
EOF
    ;;
esac

echo "Web app created: $APP_DIR"
echo "Run: cd $APP_DIR && npm install && npm run dev"