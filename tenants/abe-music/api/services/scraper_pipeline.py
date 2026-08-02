import asyncio
import logging
from datetime import datetime, timezone

logger = logging.getLogger("abe.scraper_pipeline")

class ScraperPipeline:
    def __init__(self):
        self.scrapers = []
        self.last_run = None
        self.status = "idle"

    async def run_all(self):
        self.status = "running"
        self.last_run = datetime.now(timezone.utc).isoformat()
        logger.info("Scraper pipeline starting...")
        results = {"spotify": False, "apple_music": False, "youtube": False,
                   "tiktok": False, "deezer": False, "instagram": False, "wikipedia": False}
        self.status = "complete"
        return results

    def get_status(self):
        return {
            "status": self.status,
            "last_run": self.last_run,
            "scrapers_configured": len(self.scrapers)
        }

pipeline = ScraperPipeline()
