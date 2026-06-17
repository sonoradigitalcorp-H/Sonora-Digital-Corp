"""
JARVIS Web UI — FastAPI Application
Modular: routes in webui/routes/
"""

import os
import sys
import logging
from pathlib import Path

_project_root = Path(__file__).parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s %(message)s"
)
log = logging.getLogger("jarvis.webui")

from webui.routes import app

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("JARVIS_UI_PORT", 5174))
    log.info(f"Starting JARVIS Web UI on port {port}")
    log.info(
        f"Routes: sessions, chat, files, sdc, mysticverse, payments, abe, voice, commands, webhooks"
    )
    uvicorn.run(app, host="127.0.0.1", port=port)
