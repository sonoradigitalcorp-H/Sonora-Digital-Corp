"""Cron schedule configuration for Playwright scraper [FR6].

Corre diariamente a las 6:00 AM. Configurable via env CRON_SCHEDULE.
"""

import os

CRON_SCHEDULE = os.getenv("SCRAPER_CRON", "0 6 * * *")
