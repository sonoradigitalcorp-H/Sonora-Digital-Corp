#!/bin/bash
# Web: Start development server
set -e

APP_NAME="${1:-}"
if [ -z "$APP_NAME" ]; then
  echo "Usage: $0 <app-name>"
  echo "Available apps:"
  ls sonora-digital-corp/apps/frontends/
  exit 1
fi

APP_DIR="sonora-digital-corp/apps/frontends/$APP_NAME"
if [ ! -d "$APP_DIR" ]; then
  echo "App not found: $APP_DIR"
  exit 1
fi

echo "Starting dev server for $APP_NAME"
cd "$APP_DIR"

# Detect package manager and run dev
if [ -f "pnpm-lock.yaml" ]; then
  pnpm dev
elif [ -f "yarn.lock" ]; then
  yarn dev
else
  npm run dev
fi