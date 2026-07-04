"""YouTube Collector — obtiene metricas via feed publico + Playwright fallback"""
from collectors.base import Collector, RawMetric
from datetime import datetime, timezone


class YouTubeCollector(Collector):
    platform = "youtube"

    async def collect(self, channel_id: str) -> list[RawMetric]:
        now = datetime.now(timezone.utc).isoformat()
        metrics = []

        try:
            async_data = await self._fetch_via_feed(channel_id)
            metrics.extend(async_data)
        except Exception:
            fallback = await self._fetch_via_browser(channel_id)
            metrics.extend(fallback)

        return metrics

    async def _fetch_via_feed(self, channel_id: str) -> list[RawMetric]:
        now = datetime.now(timezone.utc).isoformat()
        metrics = []

        try:
            import urllib.request
            import re

            url = f"https://www.youtube.com/@{channel_id}/about"
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode("utf-8", errors="replace")

            patterns = {
                "subscribers": r'"subscriberCount"\s*:\s*"?(\d[\d,.]*[KM]?)"?',
                "videos": r'"videoCount"\s*:\s*(\d+)',
                "views": r'"viewCount"\s*:\s*"(\d+)"',
            }
            for metric, pattern in patterns.items():
                match = re.search(pattern, html)
                if match:
                    val = match.group(1)
                    multiplier = 1
                    if val.endswith("K"):
                        multiplier = 1000
                        val = val[:-1]
                    elif val.endswith("M"):
                        multiplier = 1000000
                        val = val[:-1]
                    elif val.endswith("B"):
                        multiplier = 1000000000
                        val = val[:-1]
                    val = int(float(val.replace(",", "")) * multiplier)
                    metrics.append(RawMetric(
                        platform="youtube",
                        metric=metric,
                        value=val,
                        timestamp=now,
                        artist_id=channel_id,
                    ))
        except Exception as e:
            raise RuntimeError(f"YouTube feed failed: {e}") from e

        return metrics

    async def _fetch_via_browser(self, channel_id: str) -> list[RawMetric]:
        now = datetime.now(timezone.utc).isoformat()
        metrics = []

        try:
            from playwright.async_api import async_playwright
        except ImportError:
            raise RuntimeError("Playwright not available")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(f"https://www.youtube.com/@{channel_id}/about", timeout=15000)
            await page.wait_for_load_state("networkidle")
            text = await page.content()

            import re
            patterns = {
                "subscribers": r'"subscriberCount"\s*:\s*"(\d+)"',
                "videos": r'"videoCount"\s*:\s*(\d+)',
                "views": r'"viewCount"\s*:\s*"(\d+)"',
            }
            for metric, pattern in patterns.items():
                match = re.search(pattern, text)
                if match:
                    metrics.append(RawMetric(
                        platform="youtube",
                        metric=metric,
                        value=int(match.group(1)),
                        timestamp=now,
                        artist_id=channel_id,
                    ))

            await browser.close()

        return metrics
