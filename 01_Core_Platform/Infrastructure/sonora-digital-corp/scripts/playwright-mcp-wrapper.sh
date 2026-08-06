#!/bin/bash
export PATH="/home/mystic/.npm-global/bin:/usr/bin:/bin:$PATH"

# Auto-detect Playwright Chromium version
CHROMIUM_DIR=$(ls -d /home/mystic/.cache/ms-playwright/chromium-*/chrome-linux64/ 2>/dev/null | sort -V | tail -1)
if [ -n "$CHROMIUM_DIR" ]; then
    export PLAYWRIGHT_CHROMIUM_EXECUTABLE="${CHROMIUM_DIR}chrome"
else
    # Fallback to default
    export PLAYWRIGHT_CHROMIUM_EXECUTABLE=$(npx playwright install --dry-run 2>/dev/null | grep chromium || echo "/usr/bin/chromium-browser")
fi

exec /usr/bin/node /home/mystic/.npm-global/lib/node_modules/@playwright/mcp/cli.js --headless --browser chromium
