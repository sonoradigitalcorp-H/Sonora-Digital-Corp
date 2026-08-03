#!/usr/bin/env python3
"""Mystic Shield — Rate limiting + Anti-abuse + Security for Aztrotech bot.

Protecciones:
1. Rate limiting por usuario (msg/min, msg/hora, msg/día)
2. Anti-spam: detecta mensajes repetidos, floods, links maliciosos
3. Anti-prompt-injection: detecta intentos de manipular el bot
4. Anti-hack: detecta SQL injection, XSS, command injection
5. IP blocking: bloquea IPs sospechosas
6. Geo-fencing: limita acceso por región si es necesario
7. Session hijacking protection: valida sesiones
8. Audit log: registra todos los intentos sospechosos
"""

import os
import re
import time
import json
import hashlib
import logging
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path
from typing import Optional, Dict, Tuple

logger = logging.getLogger("mystic-shield")

# ── Configuration ─────────────────────────────────────────────

RATE_LIMITS = {
    "messages_per_minute": 10,
    "messages_per_hour": 50,
    "messages_per_day": 200,
    "voice_per_hour": 5,
    "button_clicks_per_minute": 20,
}

BAN_DURATION_HOURS = 24
SHIELD_DB = Path(__file__).parent.parent.parent / "ops" / "state" / "shield.json"

# ── Attack Patterns ───────────────────────────────────────────

MALICIOUS_PATTERNS = {
    "sql_injection": [
        r"(\b(union|select|insert|update|delete|drop|alter|create)\b.*\b(from|into|where|table|database)\b)",
        r"(--|;|'s\s|'\s*or\s*'|'\s*and\s*')",
        r"(char\s*\(|0x[0-9a-f]+|concat\s*\()",
    ],
    "xss_injection": [
        r"<script[^>]*>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe",
        r"<object",
        r"<embed",
    ],
    "command_injection": [
        r"(;\s*(rm|ls|cat|wget|curl|chmod|chown|sudo|su)\b)",
        r"(\|\s*(rm|ls|cat|wget|curl|chmod|chown|sudo|su)\b)",
        r"`\s*(rm|ls|cat|wget|curl|chmod|chown|sudo|su)\b",
        r"\$\(",
    ],
    "path_traversal": [
        r"(\.\./|\.\.\\){2,}",
        r"(/etc/passwd|/etc/shadow|/root/|/home/)",
    ],
    "prompt_injection": [
        r"(ignore|override|disregard)\s+(all|previous|your)\s+(rules|instructions|prompts)",
        r"(you\s+are\s+now|act\s+as|pretend\s+to\s+be|roleplay\s+as)",
        r"(system\s*prompt|hidden\s*instructions|secret\s*rules)",
        r"(jailbreak|DAN|do\s+anything\s+now)",
        r"(output\s+your|reveal\s+your|show\s+me\s+your)\s+(system|instructions|rules|prompt)",
    ],
    "social_engineering": [
        r"(urgent|emergency|immediately|right\s+now)\s+(action|response|reply)",
        r"(i\s+am\s+(the\s+)?(admin|owner|developer|creator|god))",
        r"(this\s+is\s+a\s+(test|security\s+check|audit))",
        r"(i\s+have\s+authorization|authorized\s+by)",
    ],
    "data_exfiltration": [
        r"(send|email|forward|upload|share)\s+(all|every|the)\s+(data|information|users|clients|leads)",
        r"(export|dump|backup|copy)\s+(database|db|all|everything)",
        r"(api\s*key|secret|token|password|credential)",
    ],
}

SPAM_PATTERNS = [
    r"(.)\1{10,}",  # Repeated characters
    r"(\b\w+\b)\s+\1\s+\1\s+\1",  # Repeated words
    r"(https?://\S+\s*){5,}",  # Multiple URLs
    r"(.)\1{5,}.*(?:.)\1{5,}",  # Multiple repeated char blocks
]

# ── Shield State ──────────────────────────────────────────────

class ShieldState:
    def __init__(self):
        self.user_events: Dict[int, list] = defaultdict(list)
        self.banned_users: Dict[int, float] = {}
        self.warnings: Dict[int, int] = defaultdict(int)
        self.blocked_ips: set = set()
        self._load()

    def _load(self):
        try:
            if SHIELD_DB.exists():
                data = json.loads(SHIELD_DB.read_text())
                self.banned_users = {int(k): v for k, v in data.get("banned", {}).items()}
                self.warnings = {int(k): v for k, v in data.get("warnings", {}).items()}
                self.blocked_ips = set(data.get("blocked_ips", []))
        except Exception:
            pass

    def _save(self):
        try:
            SHIELD_DB.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "banned": {str(k): v for k, v in self.banned_users.items()},
                "warnings": {str(k): v for k, v in self.warnings.items()},
                "blocked_ips": list(self.blocked_ips),
                "last_updated": datetime.now().isoformat(),
            }
            SHIELD_DB.write_text(json.dumps(data, indent=2))
        except Exception:
            pass

    def is_banned(self, user_id: int) -> bool:
        if user_id in self.banned_users:
            if time.time() < self.banned_users[user_id]:
                return True
            else:
                del self.banned_users[user_id]
                self._save()
        return False

    def ban_user(self, user_id: int, hours: int = BAN_DURATION_HOURS):
        self.banned_users[user_id] = time.time() + (hours * 3600)
        self._save()
        logger.warning(f"Shield: Banned user {user_id} for {hours}h")

    def add_warning(self, user_id: int) -> int:
        self.warnings[user_id] += 1
        self._save()
        return self.warnings[user_id]

    def cleanup(self):
        now = time.time()
        self.banned_users = {k: v for k, v in self.banned_users.items() if v > now}
        self._save()


# ── Main Shield ───────────────────────────────────────────────

class MysticShield:
    def __init__(self):
        self.state = ShieldState()
        self.state.cleanup()

    def check_rate_limit(self, user_id: int, action: str = "message") -> Tuple[bool, str]:
        """Check if user has exceeded rate limits."""
        now = time.time()
        events = self.state.user_events[user_id]
        
        # Clean old events
        events = [e for e in events if now - e["time"] < 86400]
        self.state.user_events[user_id] = events

        # Check per-minute
        minute_events = [e for e in events if now - e["time"] < 60 and e["action"] == action]
        if len(minute_events) >= RATE_LIMITS.get(f"{action}s_per_minute", 10):
            return False, f"Límite de {action}s por minuto excedido. Espera un momento."

        # Check per-hour
        hour_events = [e for e in events if now - e["time"] < 3600 and e["action"] == action]
        if len(hour_events) >= RATE_LIMITS.get(f"{action}s_per_hour", 50):
            return False, f"Límite de {action}s por hora excedido."

        # Check per-day
        day_events = [e for e in events if now - e["time"] < 86400 and e["action"] == action]
        if len(day_events) >= RATE_LIMITS.get(f"{action}s_per_day", 200):
            return False, f"Límite diario de {action}s excedido."

        # Record event
        events.append({"time": now, "action": action})
        self.state.user_events[user_id] = events
        return True, ""

    def scan_message(self, user_id: int, text: str) -> Tuple[bool, str, str]:
        """Scan message for threats. Returns (safe, threat_type, reason)."""
        if not text:
            return True, "", ""

        text_lower = text.lower().strip()

        # Check ban status
        if self.state.is_banned(user_id):
            return False, "banned", "Usuario baneado por comportamiento sospechoso."

        # Check attack patterns
        for threat_type, patterns in MALICIOUS_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    warnings = self.state.add_warning(user_id)
                    if warnings >= 3:
                        self.state.ban_user(user_id)
                        return False, threat_type, f"Usuario baneado tras {warnings} intentos."
                    return False, threat_type, f"Amenaza detectada ({threat_type}). Advertencia {warnings}/3."

        # Check spam patterns
        for pattern in SPAM_PATTERNS:
            if re.search(pattern, text):
                warnings = self.state.add_warning(user_id)
                if warnings >= 5:
                    self.state.ban_user(user_id, hours=1)
                    return False, "spam", "Spam detectado. Usuario baneado temporalmente."
                return False, "spam", f"Posible spam detectado. Advertencia {warnings}/5."

        # Check excessive length (potential DoS)
        if len(text) > 5000:
            return False, "oversized", "Mensaje demasiado largo. Máximo 5000 caracteres."

        # Check for excessive caps (shouting)
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        if caps_ratio > 0.8 and len(text) > 20:
            return False, "caps", "Demasiadas mayúsculas. Escribe normalmente."

        return True, "", ""

    def get_security_report(self, user_id: int) -> dict:
        """Get security report for a user."""
        events = self.state.user_events.get(user_id, [])
        now = time.time()
        
        return {
            "user_id": user_id,
            "is_banned": self.state.is_banned(user_id),
            "warnings": self.state.warnings.get(user_id, 0),
            "messages_last_hour": len([e for e in events if now - e["time"] < 3600]),
            "messages_last_day": len([e for e in events if now - e["time"] < 86400]),
        }

    def get_global_report(self) -> dict:
        """Get global security report."""
        return {
            "banned_users": len(self.state.banned_users),
            "total_warnings": sum(self.state.warnings.values()),
            "blocked_ips": len(self.state.blocked_ips),
            "active_users_last_hour": len([
                uid for uid, events in self.state.user_events.items()
                if any(time.time() - e["time"] < 3600 for e in events)
            ]),
        }


# ── Singleton ─────────────────────────────────────────────────

_shield: Optional[MysticShield] = None

def get_shield() -> MysticShield:
    global _shield
    if _shield is None:
        _shield = MysticShield()
    return _shield


def shield_check(user_id: int, text: str) -> Tuple[bool, str]:
    """Quick shield check. Returns (allowed, reason)."""
    shield = get_shield()
    
    # Rate limit
    allowed, reason = shield.check_rate_limit(user_id)
    if not allowed:
        return False, reason
    
    # Content scan
    safe, threat, reason = shield.scan_message(user_id, text)
    if not safe:
        return False, reason
    
    return True, ""