"""Global test configuration — ensures test env vars and paths before any imports."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

# Tests import from src.core.*, core.*, voice.*, webui.*
# Old flat structure → now under apps/
for p in ["apps/jarvis", "apps/jarvis/src", "apps", "apps/abe-service", "mcp", "."]:
    full = ROOT / p
    if full.exists():
        sys.path.insert(0, str(full))

# Fix: make 'apps' a namespace package so apps.abe_service resolves
# Also ensure abe-service can be found when imported as apps.abe_service
# by adding the parent dir of apps to path
_parent = str(ROOT)
if _parent not in sys.path:
    sys.path.insert(0, _parent)

# Force test mode for Mercado Pago (prevents real API calls)
os.environ["MERCADO_PAGO_ACCESS_TOKEN"] = "TEST-fake"
