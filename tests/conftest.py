"""Global test configuration — ensures test env vars and paths before any imports."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

# Tests import from core.*, apps.*, skills.mcp.*
for p in ["apps", "core", "skills/mcp", "."]:
    full = ROOT / p
    if full.exists():
        sys.path.insert(0, str(full))

_parent = str(ROOT)
if _parent not in sys.path:
    sys.path.insert(0, _parent)

# Force test mode for Mercado Pago (prevents real API calls)
os.environ["MERCADO_PAGO_ACCESS_TOKEN"] = "TEST-fake"
