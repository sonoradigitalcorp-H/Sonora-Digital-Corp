"""
YouTube Content Bot — News Scraper + Script Generator
Julian Goldie-style: trending AI news → script in 5 min
"""
import logging
import random
from datetime import datetime

import httpx

log = logging.getLogger("youtube-bot.scraper")

NEWS_SOURCES = {
    "hackernews": "https://hacker-news.firebaseio.com/v0/topstories.json",
    "producthunt": "https://api.producthunt.com/v2/api/graphql",
}

class NewsScraper:
    def __init__(self):
        self.client = httpx.Client(timeout=30)
        
    def get_trending_ai_news(self, limit: int = 10) -> list[dict]:
        """Multi-source trending AI news aggregation"""
        articles = []
        
        # HackerNews AI stories
        try:
            response = self.client.get(NEWS_SOURCES["hackernews"])
            top_ids = response.json()[:30]
            for story_id in top_ids:
                story_resp = self.client.get(
                    f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                )
                story = story_resp.json()
                if story and story.get("type") == "story":
                    title = story.get("title", "")
                    url = story.get("url", f"https://news.ycombinator.com/item?id={story_id}")
                    # Filter AI-related
                    if any(kw in title.lower() for kw in ["ai", "ml", "llm", "gpt", "neural", 
                        "deep learning", "openai", "claude", "gemini", "language model",
                        "diffusion", "transformer", "rag", "agent"]):
                        articles.append({
                            "title": title,
                            "url": url,
                            "score": story.get("score", 0),
                            "source": "hackernews",
                            "id": story_id,
                            "timestamp": datetime.now().isoformat(),
                        })
        except Exception as e:
            log.warning(f"HN scrape failed: {e}")
        
        articles.sort(key=lambda x: x.get("score", 0), reverse=True)
        return articles[:limit]

    def generate_script(self, article: dict) -> str:
        """Generate YouTube script from article (Claude would do this better)"""
        title = article.get("title", "")
        source = article.get("source", "unknown")
        
        templates = [
            f"""🔥 BREAKING: {title}

Today we're talking about something HUGE in the AI world.

[INTRODUCTION - 15 sec]
"Hey everyone, welcome back to the channel! If you're new here, we talk about AI tools and strategies that actually make you money. Today, I came across something on {source} that changes EVERYTHING..."

[MAIN CONTENT - 60-90 sec]
"So here's what happened: {title}

This is significant because...

Let me break down what this means for you..."

[ACTIONABLE INSIGHT - 30 sec]
"Here's what you need to do right now..."

[CALL TO ACTION - 15 sec]
"Like and subscribe if you want more AI news that actually matters. Drop a comment with your thoughts!"

🎬 Production notes: 
- Speed: 1.25x delivery
- Tone: Urgent but informative
- Hook in first 3 seconds
""",
            f"""🚨 AI NEWS FLASH: {title}

"Welcome back to your daily AI briefing. If you want to stay ahead of the curve, you're in the right place.

What happened: {title}

Why it matters: This is directly impacting how we build and deploy AI systems.

The opportunity: Here's how you can capitalize on this...

Like this video? Hit subscribe. We post daily AI news that actually helps you build."

⏱ Duration: ~3 min
🎯 Style: News anchor, authoritative
""",
        ]
        
        return random.choice(templates)

class ContentScheduler:
    """Manage content calendar and posting schedule"""
    def __init__(self):
        self.schedule = {
            "monday": ["research", "script", "voice", "video"],
            "tuesday": ["research", "script", "voice", "video"],
            "wednesday": ["research", "script", "voice", "video"],
            "thursday": ["research", "script", "voice", "video"],
            "friday": ["research", "script", "voice", "video"],
            "saturday": ["social clips", "shorts", "tiktok"],
            "sunday": ["rest", "analytics", "strategy"],
        }
    
    def get_today_tasks(self) -> list[str]:
        return self.schedule.get(
            datetime.now().strftime("%A").lower(),
            ["rest"]
        )

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scraper = NewsScraper()
    news = scraper.get_trending_ai_news(5)
    print(f"Found {len(news)} trending AI articles")
    for item in news[:3]:
        print(f"\n{'='*60}")
        print(f"📰 {item['title']}")
        print(f"   Score: {item.get('score', 0)} | Source: {item['source']}")
        print("\n📝 Script preview:")
        script = scraper.generate_script(item)
        print(script[:300] + "...")
