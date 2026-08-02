#!/bin/bash
# Mobile: Build mobile app
set -e

APP_NAME="${1:-}"
PLATFORM="${2:-both}"
if [ -z "$APP_NAME" ]; then
  echo "Usage: $0 <app-name> [platform]"
  echo "Platforms: ios, android, both"
  exit 1
fi

APP_DIR="sonora-digital-corp/apps/mobile/$APP_NAME"
if [ ! -d "$APP_DIR" ]; then
  echo "App not found: $APP_DIR"
  exit 1
fi

cd "$APP_DIR"

echo "Building $APP_NAME for $PLATFORM"

# Detect framework
if [ -f "pubspec.yaml" ]; then
  # Flutter
  case $PLATFORM in
    ios) flutter build ios --release ;;
    android) flutter build apk --release ;;
    both) flutter build ios --release && flutter build apk --release ;;
  esac
elif [ -f "package.json" ]; then
  # React Native / Expo
  if grep -q "expo" package.json; then
    # Expo
    case $PLATFORM in
      ios) npx expo build:ios ;;
      android) npx expo build:android ;;
      both) npx expo build:ios && npx expo build:android ;;
    esac
  else
    # React Native CLI
    case $PLATFORM in
      ios) npx react-native build-ios --configuration Release ;;
      android) npx react-native build-android --configuration Release ;;
      both) npx react-native build-ios --configuration Release && npx react-native build-android --configuration Release ;;
    esac
  fi
else
  echo "Unknown mobile framework"
  exit 1
fi

echo "Build complete!"