"""
SDC Gamification Engine — XP, niveles, badges, leaderboards.
Motores de retención y pertenencia para la plataforma Mysticverse y SDC.
"""

import json
import logging
import time
import math
from typing import Optional, Dict, List, Any

log = logging.getLogger("jarvis.gamification")

LEVELS = [
    {"level": 1, "name": "Novato", "xp_required": 0, "benefits": ["chat_basico"]},
    {
        "level": 2,
        "name": "Aprendiz",
        "xp_required": 100,
        "benefits": ["chat_ilimitado"],
    },
    {
        "level": 3,
        "name": "Explorador",
        "xp_required": 300,
        "benefits": ["fotos_extra", "badge_explorador"],
    },
    {
        "level": 4,
        "name": "Conquistador",
        "xp_required": 700,
        "benefits": ["videos_extra", "badge_conquistador"],
    },
    {
        "level": 5,
        "name": "Estratega",
        "xp_required": 1500,
        "benefits": ["contenido_exclusivo", "badge_estratega"],
    },
    {
        "level": 6,
        "name": "Visionario",
        "xp_required": 3000,
        "benefits": ["descuento_10", "badge_visionario"],
    },
    {
        "level": 7,
        "name": "Magnate",
        "xp_required": 6000,
        "benefits": ["soporte_vip", "badge_magnate"],
    },
    {
        "level": 8,
        "name": "Leyenda",
        "xp_required": 12000,
        "benefits": ["todo_acceso", "badge_leyenda", "partner"],
    },
]

BADGES = {
    "primer_mensaje": {"name": "Primer Paso", "icon": "🌱", "xp": 10},
    "streak_7": {"name": "Constante", "icon": "🔥", "xp": 100},
    "streak_30": {"name": "Inquebrantable", "icon": "💎", "xp": 500},
    "primer_lead": {"name": "Vendedor Nato", "icon": "💰", "xp": 50},
    "primera_venta": {"name": "Primer Ingreso", "icon": "💵", "xp": 200},
    "compartir_redes": {"name": "Influencer", "icon": "📢", "xp": 30},
    "referir_amigo": {"name": "Conector", "icon": "🤝", "xp": 150},
    "subir_nivel_3": {"name": "Explorador Real", "icon": "🗺️", "xp": 100},
    "subir_nivel_5": {"name": "Estratega", "icon": "🧠", "xp": 300},
    "subir_nivel_8": {"name": "Leyenda Viva", "icon": "🏆", "xp": 1000},
    "aniversario_1": {"name": "Fiel", "icon": "🎂", "xp": 500},
    "adult_verified": {"name": "Verificado", "icon": "✅", "xp": 50},
}

XP_RULES = {
    "chat_message": 10,
    "daily_login": 50,
    "streak_bonus": 20,
    "share_content": 100,
    "refer_friend": 500,
    "make_purchase": 200,
    "earn_lead": 150,
    "complete_kyc": 100,
    "rate_content": 25,
    "feedback": 75,
}


class GamificationEngine:
    def __init__(self):
        self.players: Dict[str, Dict] = {}

    def get_or_create_player(self, player_id: str, name: str = "") -> Dict:
        if player_id not in self.players:
            self.players[player_id] = {
                "id": player_id,
                "name": name,
                "xp": 0,
                "level": 1,
                "badges": [],
                "streak": 0,
                "last_login": 0,
                "created_at": time.time(),
            }
        return self.players[player_id]

    def add_xp(self, player_id: str, amount: int, reason: str = "") -> Dict:
        player = self.get_or_create_player(player_id)
        player["xp"] += amount
        old_level = player["level"]
        new_level = self._calculate_level(player["xp"])
        player["level"] = new_level

        result = {
            "player_id": player_id,
            "xp_added": amount,
            "total_xp": player["xp"],
            "level": new_level,
            "reason": reason,
            "leveled_up": new_level > old_level,
            "new_badges": [],
        }

        if result["leveled_up"]:
            level_info = self.get_level_info(new_level)
            result["level_info"] = level_info

            badge_id = f"subir_nivel_{new_level}"
            if badge_id in BADGES and badge_id not in player["badges"]:
                player["badges"].append(badge_id)
                result["new_badges"].append(BADGES[badge_id])

        return result

    def award_badge(self, player_id: str, badge_id: str) -> Dict:
        player = self.get_or_create_player(player_id)
        if badge_id not in BADGES:
            return {"error": f"Badge {badge_id} not found"}
        if badge_id in player["badges"]:
            return {"error": "Already awarded"}

        player["badges"].append(badge_id)
        badge = BADGES[badge_id]
        xp_result = self.add_xp(player_id, badge["xp"], f"Badge: {badge['name']}")

        return {
            "player_id": player_id,
            "badge": badge,
            "xp_awarded": badge["xp"],
            "total_xp": player["xp"],
        }

    def daily_login(self, player_id: str) -> Dict:
        player = self.get_or_create_player(player_id)
        now = time.time()
        DAY_SECS = 86400

        if now - player["last_login"] < DAY_SECS:
            return {"message": "Already logged in today"}

        if player["last_login"] > 0 and now - player["last_login"] < 2 * DAY_SECS:
            player["streak"] += 1
        else:
            player["streak"] = 1

        player["last_login"] = now
        xp = XP_RULES["daily_login"] + (player["streak"] * XP_RULES["streak_bonus"])
        result = self.add_xp(player_id, xp, "Daily login")

        if player["streak"] == 7 and "streak_7" not in player["badges"]:
            self.award_badge(player_id, "streak_7")
        if player["streak"] >= 30 and "streak_30" not in player["badges"]:
            self.award_badge(player_id, "streak_30")

        result["streak"] = player["streak"]
        return result

    def track_action(self, player_id: str, action: str) -> Dict:
        if action in XP_RULES:
            return self.add_xp(player_id, XP_RULES[action], action)

        action_badges = {
            "first_message": "primer_mensaje",
            "first_lead": "primer_lead",
            "first_sale": "primera_venta",
            "shared": "compartir_redes",
            "referred": "referir_amigo",
            "kyc_done": "adult_verified",
        }
        if action in action_badges:
            return self.award_badge(player_id, action_badges[action])

        return {"message": f"Unknown action: {action}"}

    def get_player(self, player_id: str) -> Optional[Dict]:
        return self.players.get(player_id)

    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        sorted_players = sorted(
            self.players.values(),
            key=lambda p: p["xp"],
            reverse=True,
        )
        return [
            {
                "rank": i + 1,
                "id": p["id"],
                "name": p["name"],
                "level": p["level"],
                "xp": p["xp"],
                "badges": len(p["badges"]),
                "streak": p["streak"],
            }
            for i, p in enumerate(sorted_players[:limit])
        ]

    def _calculate_level(self, xp: int) -> int:
        level = 1
        for lvl in reversed(LEVELS):
            if xp >= lvl["xp_required"]:
                level = lvl["level"]
                break
        return level

    def get_level_info(self, level: int) -> Optional[Dict]:
        for lvl in LEVELS:
            if lvl["level"] == level:
                return lvl
        return None

    def get_all_badges(self, player_id: str) -> List[Dict]:
        player = self.get_or_create_player(player_id)
        return [
            {**BADGES[bid], "id": bid, "awarded": bid in player["badges"]}
            for bid in BADGES
        ]


# Singleton
_engine: Optional[GamificationEngine] = None


def get_engine() -> GamificationEngine:
    global _engine
    if _engine is None:
        _engine = GamificationEngine()
    return _engine
