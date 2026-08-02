#!/bin/bash
# Mobile: Create mobile app
set -e

APP_NAME="${1:-}"
FRAMEWORK="${2:-react-native}"
if [ -z "$APP_NAME" ]; then
  echo "Usage: $0 <app-name> [framework]"
  echo "Frameworks: react-native, expo, flutter, ionic"
  exit 1
fi

APP_DIR="sonora-digital-corp/apps/mobile/$APP_NAME"
mkdir -p "$APP_DIR"

echo "Creating $FRAMEWORK mobile app: $APP_NAME"

case $FRAMEWORK in
  react-native|expo)
    npx create-expo-app@latest "$APP_DIR" --template blank-typescript
    ;;
  flutter)
    flutter create "$APP_DIR" --org com.sonora-digital
    ;;
  ionic)
    npx @ionic/cli start "$APP_DIR" blank --type=angular
    ;;
  *)
    echo "Unknown framework: $FRAMEWORK"
    exit 1
    ;;
esac

echo "Mobile app created: $APP_DIR"
echo "Run: cd $APP_DIR && npm run dev (or flutter run)"