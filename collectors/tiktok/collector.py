"""TikTok Collector — obtiene metricas via Playwright (perfil publico)"""
from collectors.base import Collector, RawMetric
from datetime import datetime, timezone


class TikTokCollector(Collector):
    platform = "tiktok"

    async def collect(self, username: str) -> list[RawMetric]:
        now = datetime.now(timezone.utc).isoformat()
        metrics = []

        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(f"https://www.tiktok.com/@{username}", timeout=15000)
                await page.wait_for_load_state("networkidle")
                await page.wait_for_timeout(2000)
                text = await page.content()

                import re
                patterns = {
                    "followers": r'"followerCount"\s*:\s*(\d+)',
                    "likes": r'"heartCount"\s*:\s*(\d+)',
                    "videos": r'"videoCount"\s*:\s*(\d+)',
                }
                for metric, pattern in patterns.items():
                    match = re.search(pattern, text)
                    if match:
                        metrics.append(RawMetric(
                            platform="tiktok",
                            metric=metric,
                            value=int(match.group(1)),
                            timestamp=now,
                            artist_id=username,
                        ))

                await browser.close()
        except ImportError:
            raise RuntimeError("Playwright not available for TikTok collector")
        except Exception as e:
            raise RuntimeError(f"TikTok collect failed: {e}") from e

        return metrics
