"""WhatsApp sender via wacli binary."""

import os
import subprocess
from pathlib import Path

WACLI_BIN = os.environ.get("WACLI_PATH") or str(Path.home() / ".local" / "bin" / "wacli")
if not os.path.exists(WACLI_BIN):
    WACLI_BIN = "/usr/local/bin/wacli"


def send_whatsapp(jid: str, message: str) -> tuple[bool, str]:
    """Send a text message via WhatsApp. Returns (success, error_or_ok)."""
    if "@s.whatsapp.net" not in jid:
        jid = f"{jid}@s.whatsapp.net"
    try:
        result = subprocess.run(
            [WACLI_BIN, "send", "text", "--to", jid, "--message", message],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, result.stderr.strip()[:200]
    except subprocess.TimeoutExpired:
        return False, "timeout al enviar mensaje"
    except FileNotFoundError:
        return False, "wacli no encontrado"
    except Exception as e:
        return False, str(e)
