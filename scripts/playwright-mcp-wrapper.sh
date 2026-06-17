#!/bin/bash
export PATH="/home/mystic/.npm-global/bin:/usr/bin:/bin:$PATH"
export PLAYWRIGHT_CHROMIUM_EXECUTABLE="/home/mystic/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome"
exec /usr/bin/node /home/mystic/.npm-global/lib/node_modules/@playwright/mcp/cli.js --headless --browser chromium --port 18990
