import os
import sqlite3
from pathlib import Path

DB_DIR = Path(__file__).parent.parent / "Databases"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "froy_campana_leads.db"

TOKEN = os.environ.get("TELEGRAM_FROY_TOKEN") or ""
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY") or ""
API_URL = f"https://api.telegram.org/bot{TOKEN}" if TOKEN else ""

# ... resto del archivo original sin secret hardcoded
