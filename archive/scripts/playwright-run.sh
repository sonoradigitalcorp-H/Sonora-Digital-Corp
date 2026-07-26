#!/bin/bash
# Playwright E2E test runner for SDC App
# Opens browser on correct monitor (XWAYLAND1: 1360x768)
cd "$(dirname "$0")/.."
export DISPLAY=:0
npx playwright test --headed "$@" 2>&1
