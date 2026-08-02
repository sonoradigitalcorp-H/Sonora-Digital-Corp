#!/bin/bash
# Web: Deploy web application
set -e

APP_NAME="${1:-}"
TARGET="${2:-vercel}"
if [ -z "$APP_NAME" ]; then
  echo "Usage: $0 <app-name> [target]"
  echo "Targets: vercel, netlify, aws, docker, kubernetes"
  exit 1
fi

APP_DIR="sonora-digital-corp/apps/frontends/$APP_NAME"
if [ ! -d "$APP_DIR" ]; then
  echo "App not found: $APP_DIR"
  exit 1
fi

echo "Deploying $APP_NAME to $TARGET"

cd "$APP_DIR"

case $TARGET in
  vercel)
    npx vercel --prod
    ;;
  netlify)
    npm run build
    npx netlify deploy --prod --dir=dist
    ;;
  docker)
    docker build -t $APP_NAME .
    docker tag $APP_NAME registry.example.com/$APP_NAME:latest
    docker push registry.example.com/$APP_NAME:latest
    ;;
  *)
    echo "Unknown target: $TARGET"
    exit 1
    ;;
esac

echo "Deployment complete!"