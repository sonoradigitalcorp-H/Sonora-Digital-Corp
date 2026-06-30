"""
JARVIS Web UI — FastAPI Application
Modular: routes in webui/routes/
"""

import logging
import os
import sys
from pathlib import Path

_project_root = Path(__file__).parent.parent
_jarvis_root = _project_root / "jarvis"
sys.path.insert(0, str(_project_root))
sys.path.insert(0, str(_jarvis_root))

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
        "Routes: sessions, chat, files, sdc, mysticverse, payments, abe, voice, commands, webhooks"
    )
    uvicorn.run(app, host="127.0.0.1", port=port)
