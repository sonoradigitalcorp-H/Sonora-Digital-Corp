# conftest.py — Sonora Digital Corp (03_Sandbox_and_RnD/tests/integration)
# Hace visibles los módulos del repo para pytest (fix lección 2026-08-10:
# sys.path dentro del test no aplica → ModuleNotFoundError)

import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[3]  # raíz del repo

for p in [
    BASE / "02_Client_Projects" / "Aztrotech" / "03_Media_Assets",
    BASE / "01_Core_Platform" / "03_Agentic_Infrastructure",
    BASE / "01_Core_Platform" / "05_Shared_Libraries" / "SDK_Python",
    BASE / "01_Core_Platform" / "03_Agentic_Infrastructure" / "Databases" / "OKF_Knowledge",
    BASE / "02_Client_Projects" / "Aztrotech" / "02_Source_Code",
]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))