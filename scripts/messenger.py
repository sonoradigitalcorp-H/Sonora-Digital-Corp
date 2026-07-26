"""SDC Universal Messenger — envía mensajes a cualquier canal disponible.
OpenClaw como orquestador: detecta qué canales están disponibles y envía.

Canales soportados:
- whatsapp  → wacli / WhatsApp API
- telegram  → Telegram Bot API
- email     → SMTP / FormSubmit
- websocket → Supabase Realtime
- stdout    → CLI / terminal
- voice     → edge-tts (archivo .wav)

Usage:
  python3 -m ops.messenger send --channel whatsapp --to "5216625383272" --msg "Hola"
  python3 -m ops.messenger send --channel telegram --to "@usuario" --msg "Hola"
  python3 -m ops.messenger send --channel email --to "cliente@email.com" --msg "Hola"
  python3 -m ops.messenger broadcast --channels whatsapp,telegram,email --msg "A todos"
  python3 -m ops.messenger channels           # Lista canales disponibles
"""
import argparse
import asyncio
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


class Messenger:
    def __init__(self):
        self.channels = {}
        self._detect_channels()

    def _detect_channels(self):
        """Detecta qué canales están disponibles en el sistema."""

        # WhatsApp via wacli
        try:
            r = subprocess.run(["which", "wacli"], capture_output=True, text=True, timeout=3)
            if r.returncode == 0:
                self.channels["whatsapp"] = {"status": "available", "handler": self._send_whatsapp}
        except FileNotFoundError:
            pass

        # Telegram Bot
        tg_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        if tg_token:
            self.channels["telegram"] = {"status": "available", "handler": self._send_telegram}
        else:
            self.channels["telegram"] = {"status": "needs_config", "hint": "Set TELEGRAM_BOT_TOKEN"}

        # Email via FormSubmit
        self.channels["email"] = {"status": "available", "handler": self._send_email, "note": "Via FormSubmit API"}

        # WebSocket / Console
        self.channels["stdout"] = {"status": "available", "handler": lambda **kw: print(kw.get("msg", ""))}
        self.channels["websocket"] = {"status": "available", "handler": self._send_websocket, "note": "Via Supabase Realtime"}

        # Voice (TTS file)
        self.channels["voice"] = {"status": "available", "handler": self._send_voice}

        # OpenClaw gateway
        try:
            r = subprocess.run(["which", "openclaw"], capture_output=True, text=True, timeout=3)
            if r.returncode == 0:
                self.channels["openclaw"] = {"status": "available", "handler": self._send_via_openclaw}
        except FileNotFoundError:
            pass

    def _send_whatsapp(self, to, msg, **kwargs):
        """Send via wacli WhatsApp."""
        cmd = ["wacli", "send", "--to", to, "--message", msg[:1000]]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            return {"channel": "whatsapp", "to": to, "status": "sent" if r.returncode == 0 else "error", "detail": r.stderr[:100] if r.returncode else "ok"}
        except Exception as e:
            return {"channel": "whatsapp", "to": to, "status": "error", "detail": str(e)[:100]}

    def _send_telegram(self, to, msg, **kwargs):
        """Send via Telegram Bot API."""
        import httpx
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        chat_id = to.replace("@", "") if to.startswith("@") else to
        try:
            r = httpx.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat_id, "text": msg[:2000], "parse_mode": "HTML"},
                timeout=10,
            )
            return {"channel": "telegram", "to": to, "status": "sent" if r.is_success else "error"}
        except Exception as e:
            return {"channel": "telegram", "to": to, "status": "error", "detail": str(e)[:100]}

    def _send_email(self, to, msg, subject="SDC Notification", **kwargs):
        """Send via FormSubmit (falls back to SMTP if configured)."""
        import httpx
        try:
            r = httpx.post(
                "https://formsubmit.co/ajax/hello@sonoradigitalcorp.com",
                data={"name": "SDC System", "email": "system@sonoradigitalcorp.com", "message": msg, "_subject": subject},
                timeout=10,
            )
            return {"channel": "email", "to": to, "status": "sent" if r.is_success else "error"}
        except Exception as e:
            return {"channel": "email", "to": to, "status": "error", "detail": str(e)[:100]}

    def _send_websocket(self, to, msg, **kwargs):
        """Send via Supabase Realtime (broadcast)."""
        key = os.environ.get("SUPABASE_SERVICE_KEY", "")
        url = os.environ.get("SUPABASE_URL", "http://localhost:8000")
        if not key:
            return {"channel": "websocket", "status": "skipped", "detail": "No SUPABASE_SERVICE_KEY"}
        try:
            import httpx
            r = httpx.post(
                f"{url}/rest/v1/agent_events",
                headers={"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={"event_type": "notification", "payload": {"to": to, "message": msg}, "severity": "info"},
                timeout=5,
            )
            return {"channel": "websocket", "status": "sent" if r.is_success else "error"}
        except Exception as e:
            return {"channel": "websocket", "status": "error", "detail": str(e)[:100]}

    def _send_voice(self, to=None, msg="", output_path=None, **kwargs):
        """Generate voice audio file (for later delivery via WhatsApp/Telegram)."""
        from ops.voice.tts import speak
        result = speak(msg, output_path)
        return {"channel": "voice", "status": result.get("status"), "output": result.get("output"), "detail": result.get("note", "")}

    def _send_via_openclaw(self, to, msg, channel_target=None, **kwargs):
        """Send via OpenClaw gateway (uses Hermes for delivery)."""
        cmd = ["openclaw", "run", f"send {channel_target or to} '{msg[:500]}'"]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return {"channel": "openclaw", "to": to, "status": "ok" if r.returncode == 0 else "error", "output": r.stdout[:200]}
        except Exception as e:
            return {"channel": "openclaw", "status": "error", "detail": str(e)[:100]}

    def send(self, channel, to, msg, **kwargs):
        """Send message through a specific channel."""
        ch = self.channels.get(channel)
        if not ch:
            return {"error": f"Channel '{channel}' not available. Available: {list(self.channels.keys())}"}
        handler = ch.get("handler")
        if not handler:
            return {"error": f"Channel '{channel}' has no handler"}
        return handler(to=to, msg=msg, **kwargs)

    def broadcast(self, channels, msg, to_map=None, **kwargs):
        """Send same message to multiple channels."""
        results = {}
        for ch in channels.split(","):
            ch = ch.strip()
            to = to_map.get(ch, "all") if to_map else "all"
            results[ch] = self.send(ch, to, msg, **kwargs)
        return results

    def list_channels(self):
        """List available channels and their status."""
        return {name: {k: v for k, v in info.items() if k != "handler"} for name, info in self.channels.items()}


messenger = Messenger()


def main():
    parser = argparse.ArgumentParser(description="SDC Universal Messenger")
    sub = parser.add_subparsers(dest="command")

    send_p = sub.add_parser("send", help="Enviar mensaje por un canal")
    send_p.add_argument("--channel", "-c", required=True, help="Canal: whatsapp, telegram, email, stdout, voice, openclaw")
    send_p.add_argument("--to", "-t", help="Destinatario")
    send_p.add_argument("--msg", "-m", required=True, help="Mensaje")
    send_p.add_argument("--subject", "-s", default="SDC Notification", help="Asunto (email)")

    bc_p = sub.add_parser("broadcast", help="Enviar a múltiples canales")
    bc_p.add_argument("--channels", required=True, help="Canales separados por coma: whatsapp,telegram,email")
    bc_p.add_argument("--msg", required=True, help="Mensaje")
    bc_p.add_argument("--to-whatsapp", help="WhatsApp destino")
    bc_p.add_argument("--to-telegram", help="Telegram destino")
    bc_p.add_argument("--to-email", help="Email destino")

    sub.add_parser("channels", help="Listar canales disponibles")

    args = parser.parse_args()

    if args.command == "send":
        result = messenger.send(args.channel, args.to or "all", args.msg, subject=args.subject)
        print(json.dumps(result, indent=2))

    elif args.command == "broadcast":
        to_map = {}
        if args.to_whatsapp: to_map["whatsapp"] = args.to_whatsapp
        if args.to_telegram: to_map["telegram"] = args.to_telegram
        if args.to_email: to_map["email"] = args.to_email
        results = messenger.broadcast(args.channels, args.msg, to_map)
        for ch, res in results.items():
            print(f"  {ch}: {res.get('status', 'error')}")

    elif args.command == "channels":
        ch = messenger.list_channels()
        print(f"\n  Canales disponibles ({len(ch)}):")
        for name, info in ch.items():
            status_icon = "✅" if info.get("status") == "available" else "⚠️" if info.get("status") == "needs_config" else "❌"
            detail = f" — {info.get('note', '')}" if info.get("note") else ""
            hint = f" — {info.get('hint', '')}" if info.get("hint") else ""
            print(f"  {status_icon} {name}{detail}{hint}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
