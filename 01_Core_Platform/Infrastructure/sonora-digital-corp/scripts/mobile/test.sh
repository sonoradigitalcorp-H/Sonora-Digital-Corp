#!/bin/bash
# Mobile: Run mobile app tests
set -e

APP_NAME="${1:-}"
if [ -z "$APP_NAME" ]; then
  echo "Usage: $0 <app-name>"
  exit 1
fi

APP_DIR="sonora-digital-corp/apps/mobile/$APP_NAME"
if [ ! -d "$APP_DIR" ]; then
  echo "App not found: $APP_DIR"
  exit 1
fi

cd "$APP_DIR"

echo "Running tests for $APP_NAME"

# Detect framework and run appropriate tests
if [ -f "pubspec.yaml" ]; then
  # Flutter
  flutter test
elif [ -f "package.json" ]; then
  # React Native / Expo
  if [ -f "jest.config.js" ] || [ -f "jest.config.ts" ] || grep -q "jest" package.json; then
    npm test
  else
    echo "No test configuration found. Add jest or use: npx react-native test"
  fi
else
  echo "Unknown mobile framework"
  exit 1
fi

echo "Tests complete!"