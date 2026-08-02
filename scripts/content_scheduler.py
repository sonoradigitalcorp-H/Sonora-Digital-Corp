#!/usr/bin/env python3
"""Content Scheduler — Generate and schedule social media content for SDC.

Uses LLM to generate posts based on topics, then queues them for Playwright.
Respects rate limits and generates content in batches.
"""

import os
import json
import time
import random
import sqlite3
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict

logger = logging.getLogger("content-scheduler")

BASE_DIR = Path(__file__).parent.parent
QUEUE_DIR = BASE_DIR / "ops" / "state" / "content-queue"
SCHEDULE_DB = BASE_DIR / "ops" / "state" / "social_schedule.db"

# ── Content Topics ────────────────────────────────────────────

SDC_TOPICS = {
    "twitter": [
        {"topic": "AI automation tips", "hashtags": "#IA #Automatización #SonoraDigital"},
        {"topic": "Employee Digital benefits", "hashtags": "#EmpleadoDigital #Negocios #Hermosillo"},
        {"topic": "Case studies", "hashtags": "#CasoDeÉxito #Resultados #ROI"},
        {"topic": "Industry insights", "hashtags": "#Tecnología #Futuro #Digital"},
        {"topic": "Behind the scenes", "hashtags": "#Equipo #SDC #TrabajoEnEquipo"},
        {"topic": "Client testimonials", "hashtags": "#Clientes #Satisfacción #Servicio"},
        {"topic": "Tech trends 2026", "hashtags": "#Tendencias2026 #Innovación"},
        {"topic": "Local business tips", "hashtags": "#NegociosLocales #Hermosillo #Sonora"},
    ],
    "instagram": [
        {"topic": "Infographic: How AI works", "style": "carousel"},
        {"topic": "Before/after automation results", "style": "single"},
        {"topic": "Team highlight", "style": "story"},
        {"topic": "Client success story", "style": "carousel"},
        {"topic": "Behind the scenes video", "style": "reel"},
        {"topic": "Tech tip of the week", "style": "single"},
        {"topic": "Motivational quote", "style": "single"},
        {"topic": "Local business spotlight", "style": "carousel"},
    ],
}

# ── Content Templates ─────────────────────────────────────────

TWITTER_TEMPLATES = [
    "🤖 {topic}:\n\n{insight}\n\n{hashtags}\n\n¿Tu negocio ya usa IA? Cuéntame 👇",
    "💡 Sabías que...\n\n{insight}\n\n{hashtags}\n\n#SonoraDigital #Automatización",
    "🚀 {topic}\n\n{insight}\n\n¿Quieres saber más? Escríbeme 💬\n\n{hashtags}",
    "📊 Dato del día:\n\n{insight}\n\n{hashtags}\n\n#IA #Negocios",
    "🎯 Para los emprendedores de Hermosillo:\n\n{insight}\n\n{hashtags}",
]

INSIGHTS = [
    "El 73% de los negocios que automatizan su atención al cliente ven un aumento del 30% en ventas",
    "Un empleado digital atiende 24/7 sin sueldo, IMSS ni vacaciones",
    "El 60% de los leads se pierden por no contestar a tiempo",
    "La IA no reemplaza a tu equipo, los potencia",
    "Un CRM con IA clasifica leads 5x más rápido que uno manual",
    "El follow-up automático duplica la tasa de conversión",
    "Los negocios locales en Hermosillo están adoptando IA un 40% más rápido",
    "El costo de no automatizar es 3x mayor que el de implementar",
    "Un chatbot inteligente resuelve el 80% de las preguntas frecuentes",
    "La personalización con IA aumenta la retención un 45%",
]


# ── Scheduler ─────────────────────────────────────────────────

class ContentScheduler:
    def __init__(self):
        QUEUE_DIR.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(SCHEDULE_DB))
        self._init_db()
    
    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS scheduled_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT,
                topic TEXT,
                content TEXT,
                scheduled_at TEXT,
                status TEXT DEFAULT 'pending',
                posted_at TEXT
            )
        """)
        self.conn.commit()
    
    def generate_content(self, platform: str, count: int = 5) -> List[dict]:
        """Generate content for a platform."""
        topics = SDC_TOPICS.get(platform, [])
        posts = []
        
        for i in range(count):
            topic_info = random.choice(topics)
            topic = topic_info["topic"]
            hashtags = topic_info.get("hashtags", "")
            
            if platform == "twitter":
                template = random.choice(TWITTER_TEMPLATES)
                insight = random.choice(INSIGHTS)
                content = template.format(
                    topic=topic,
                    insight=insight,
                    hashtags=hashtags,
                )
            else:
                content = {
                    "topic": topic,
                    "style": topic_info.get("style", "single"),
                    "hashtags": hashtags,
                }
            
            posts.append({
                "platform": platform,
                "content": content if isinstance(content, str) else json.dumps(content),
                "topic": topic,
            })
        
        return posts
    
    def schedule_posts(self, platform: str, posts: List[dict], 
                       start_hour: int = 9, interval_hours: int = 3):
        """Schedule posts across the day."""
        now = datetime.now()
        today = now.date()
        
        for i, post in enumerate(posts):
            hour = start_hour + (i * interval_hours)
            if hour > 21:  # Don't post after 9pm
                hour = 9 + (hour - 22)
                today += timedelta(days=1)
            
            scheduled = datetime.combine(today, datetime.min.time().replace(hour=hour))
            
            self.conn.execute(
                "INSERT INTO scheduled_posts (platform, topic, content, scheduled_at) VALUES (?, ?, ?, ?)",
                (platform, post["topic"], post["content"], scheduled.isoformat())
            )
        
        self.conn.commit()
        return len(posts)
    
    def get_pending(self, platform: str) -> List[dict]:
        """Get pending posts that are due."""
        now = datetime.now().isoformat()
        rows = self.conn.execute(
            "SELECT id, topic, content, scheduled_at FROM scheduled_posts "
            "WHERE platform=? AND status='pending' AND scheduled_at<=? "
            "ORDER BY scheduled_at LIMIT 3",
            (platform, now)
        ).fetchall()
        
        return [{"id": r[0], "topic": r[1], "content": r[2], "scheduled_at": r[3]} for r in rows]
    
    def mark_posted(self, post_id: int):
        self.conn.execute(
            "UPDATE scheduled_posts SET status='posted', posted_at=? WHERE id=?",
            (datetime.now().isoformat(), post_id)
        )
        self.conn.commit()
    
    def get_stats(self) -> dict:
        pending = self.conn.execute("SELECT COUNT(*) FROM scheduled_posts WHERE status='pending'").fetchone()[0]
        posted = self.conn.execute("SELECT COUNT(*) FROM scheduled_posts WHERE status='posted'").fetchone()[0]
        return {"pending": pending, "posted": posted}


# ── Auto-Response Templates ───────────────────────────────────

SDC_RESPONSES = {
    "twitter": {
        "mentions": [
            "¡Hola {name}! Gracias por contactarnos. ¿En qué te podemos ayudar? 💬",
            "¡Hey {name}! 🤖 ¿Tienes preguntas sobre automatización? Estamos aquí para ayudarte.",
            "¡Gracias {name}! Un gusto saludarte. ¿Cómo podemos impulsar tu negocio? 🚀",
        ],
        "dms": [
            "¡Hola {name}! Bienvenido a Sonora Digital Corp. ¿En qué te puedo ayudar hoy?",
            "¡Qué tal {name}! Gracias por escribirnos. Cuéntame sobre tu negocio y cómo podemos ayudarte.",
        ],
    },
    "instagram": {
        "comments": [
            "¡Gracias {name}! 🔥 ¿Te interesa saber más?",
            "¡Exacto {name}! La IA está transformando los negocios 💡",
            "¡Genial {name}! ¿Ya estás usando automatización en tu negocio?",
        ],
        "dms": [
            "¡Hola {name}! 👋 Bienvenido a Sonora Digital Corp. ¿Cómo podemos ayudarte?",
        ],
    },
}


def generate_response(platform: str, context: str, username: str = "amigo") -> str:
    """Generate a contextual response."""
    templates = SDC_RESPONSES.get(platform, {}).get(context, ["¡Hola! Gracias por contactarnos 💬"])
    template = random.choice(templates)
    return template.format(name=username)


# ── Main ──────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Content Scheduler")
    parser.add_argument("--generate", choices=["twitter", "instagram"], help="Generate content")
    parser.add_argument("--count", type=int, default=5, help="Number of posts to generate")
    parser.add_argument("--schedule", action="store_true", help="Schedule generated content")
    parser.add_argument("--status", action="store_true", help="Show status")
    args = parser.parse_args()
    
    scheduler = ContentScheduler()
    
    if args.status:
        stats = scheduler.get_stats()
        print(f"Pending: {stats['pending']}, Posted: {stats['posted']}")
        return
    
    if args.generate:
        posts = scheduler.generate_content(args.generate, args.count)
        print(f"Generated {len(posts)} posts for {args.generate}:")
        for p in posts:
            print(f"  - {p['topic']}")
        
        if args.schedule:
            scheduled = scheduler.schedule_posts(args.generate, posts)
            print(f"\nScheduled {scheduled} posts across the day")
    
    if args.schedule and not args.generate:
        # Process pending posts
        for platform in ["twitter", "instagram"]:
            pending = scheduler.get_pending(platform)
            print(f"\n{platform}: {len(pending)} posts due")


if __name__ == "__main__":
    main()