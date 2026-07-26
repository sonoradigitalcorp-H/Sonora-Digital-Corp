"""Spotify Collector — obtiene metricas via API publica + Playwright fallback"""
from collectors.base import Collector, RawMetric
from datetime import datetime, timezone


class SpotifyCollector(Collector):
    platform = "spotify"

    async def collect(self, artist_id: str) -> list[RawMetric]:
        metrics = []
        now = datetime.now(timezone.utc).isoformat()

        try:
            async_data = await self._fetch_via_api(artist_id)
            metrics.extend(async_data)
        except Exception:
            fallback = await self._fetch_via_browser(artist_id)
            metrics.extend(fallback)

        return metrics

    async def _fetch_via_api(self, artist_id: str) -> list[RawMetric]:
        now = datetime.now(timezone.utc).isoformat()
        metrics = []

        try:
            import urllib.request
            import json

            url = f"https://open.spotify.com/artist/{artist_id}"
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode("utf-8", errors="replace")

            import re
            patterns = {
                "monthly_listeners": r'"monthlyListeners"\s*:\s*(\d+)',
                "followers": r'"followers"\s*:\s*(\d+)',
                "popularity": r'"popularity"\s*:\s*(\d+)',
            }
            for metric, pattern in patterns.items():
                match = re.search(pattern, html)
                if match:
                    metrics.append(RawMetric(
                        platform="spotify",
                        metric=metric,
                        value=int(match.group(1)),
                        timestamp=now,
                        artist_id=artist_id,
                    ))
        except Exception as e:
            raise RuntimeError(f"Spotify API scrape failed: {e}") from e

        return metrics

    async def _fetch_via_browser(self, artist_id: str) -> list[RawMetric]:
        now = datetime.now(timezone.utc).isoformat()
        metrics = []

        try:
            from playwright.async_api import async_playwright
        except ImportError:
            raise RuntimeError("Playwright not available for browser fallback")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(f"https://open.spotify.com/artist/{artist_id}", timeout=15000)
            await page.wait_for_load_state("networkidle")

            text = await page.content()
            import re
            for metric, pattern in {
                "monthly_listeners": r'"monthlyListeners"\s*:\s*(\d+)',
                "followers": r'"followers"\s*:\s*(\d+)',
                "popularity": r'"popularity"\s*:\s*(\d+)',
            }.items():
                match = re.search(pattern, text)
                if match:
                    metrics.append(RawMetric(
                        platform="spotify",
                        metric=metric,
                        value=int(match.group(1)),
                        timestamp=now,
                        artist_id=artist_id,
                    ))

            await browser.close()

        return metrics
