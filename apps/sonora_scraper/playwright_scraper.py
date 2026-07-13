"""Playwright Scraping Pipeline [FR6] — extracción diaria de métricas via headless browser.

Sin APIs externas. Playwright navega como usuario normal, extrae datos,
y los almacena en scraped_metrics via Hasura.
"""

import json
import logging
import os
from typing import Any

log = logging.getLogger("sonora.scraper")

RETRY_ATTEMPTS = int(os.getenv("SCRAPER_RETRY_ATTEMPTS", "3"))
RETRY_DELAY = int(os.getenv("SCRAPER_RETRY_DELAY", "30"))  # seconds


def get_artists_to_scrape() -> list[dict[str, Any]]:
    """Get list of artists to scrape from Hasura."""
    try:
        from sonora_engine.hasura import query

        result = query("""
            query GetArtistsForScraping {
                users(where: {role: {_eq: "artist"}, is_active: {_eq: true}}) {
                    id
                    display_name
                    metadata
                    tenant_id
                }
            }
        """)

        artists = []
        for u in result.get("data", {}).get("users", []):
            metadata = u.get("metadata", {})
            spotify_url = metadata.get("spotify_url", "")
            if spotify_url:
                artists.append({
                    "id": u["id"],
                    "name": u["display_name"],
                    "url": spotify_url,
                    "tenant_id": u["tenant_id"],
                })
        return artists
    except Exception:
        return []  # Fallback for tests / unavailable Hasura


def scrape_artist(browser: Any, artist_name: str, url: str) -> dict[str, Any] | None:
    """Scrape metrics for a single artist using Playwright.

    Args:
        browser: Playwright browser instance
        artist_name: Name of the artist
        url: URL to scrape (e.g., Spotify artist page)

    Returns:
        Dict with scraped metrics or None on failure
    """
    import asyncio

    for attempt in range(RETRY_ATTEMPTS):
        try:
            # Create new browser context and page
            context = asyncio.run(browser.new_context())
            page = asyncio.run(context.new_page())
            asyncio.run(page.goto(url, wait_until="networkidle", timeout=30000))

            # Extract metrics from page
            title = asyncio.run(page.text_content("h1")) or artist_name

            # Monthly listeners (Spotify-specific selector)
            listeners_el = asyncio.run(
                page.text_content("[data-testid='monthly-listeners']")
            ) or "0"

            # Followers
            followers_el = asyncio.run(
                page.text_content("[data-testid='followers']")
            ) or "0"

            # Top songs
            top_songs = []
            for i in range(1, 4):
                song = asyncio.run(
                    page.text_content(f"[data-testid='top-song-{i}']")
                )
                if song:
                    top_songs.append(song)

            result = {
                "artist_name": title,
                "monthly_listeners": _parse_number(listeners_el),
                "followers": _parse_number(followers_el),
                "top_songs": top_songs,
                "scraped_at": __import__("datetime").datetime.now().isoformat(),
            }

            asyncio.run(page.close())
            asyncio.run(context.close())

            return result

        except Exception as e:
            log.warning(f"Attempt {attempt + 1}/{RETRY_ATTEMPTS} failed for {artist_name}: {e}")
            if attempt < RETRY_ATTEMPTS - 1:
                __import__("time").sleep(RETRY_DELAY)
            else:
                log.error(f"All {RETRY_ATTEMPTS} attempts failed for {artist_name}")

    return None


def store_metrics(
    tenant_id: str,
    artist_id: str,
    source: str,
    metrics: dict[str, Any],
) -> bool:
    """Store scraped metrics in Hasura."""
    try:
        from sonora_engine.hasura import mutate

        for metric_name, metric_value in metrics.items():
            if metric_name in ("artist_name", "top_songs", "scraped_at"):
                continue

            mutate("""
                mutation InsertMetric($metric: scraped_metrics_insert_input!) {
                    insert_scraped_metrics_one(object: $metric) {
                        id
                    }
                }
            """, {
                "metric": {
                    "tenant_id": tenant_id,
                    "artist_id": artist_id,
                    "source": source,
                    "metric_name": metric_name,
                    "metric_value": float(metric_value),
                    "metric_unit": "count",
                    "raw_data": json.dumps(metrics),
                }
            })

        return True
    except Exception as e:
        log.error(f"Store metrics failed: {e}")
        return False


def emit_event(event_type: str, **kwargs) -> bool:
    """Emit event to Redis for WebSocket streaming."""
    import json

    try:
        import redis

        r = redis.Redis.from_url(
            os.getenv("REDIS_URL", "redis://localhost:6379/0")
        )
        r.publish(
            "agent:events",
            json.dumps({"event_type": event_type, **kwargs}),
        )
        return True
    except Exception as e:
        log.error(f"Event emit failed: {e}")
        return False


def safe_scrape(artist_name: str, url: str) -> dict[str, Any] | None:
    """Wrapper that handles all errors gracefully."""
    try:
        from playwright.async_api import async_playwright

        import asyncio

        async def _scrape():
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                try:
                    result = scrape_artist(browser, artist_name, url)
                    return result
                finally:
                    await browser.close()

        return asyncio.run(_scrape())
    except Exception as e:
        log.error(f"safe_scrape failed for {artist_name}: {e}")
        return None


def run():
    """Main entry point — scrape all artists and store results."""
    import asyncio

    async def _run():
        artists = get_artists_to_scrape()
        log.info(f"Starting scrape for {len(artists)} artists")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)

            for artist in artists:
                log.info(f"Scraping {artist['name']}...")
                result = scrape_artist(browser, artist["name"], artist["url"])
                if result:
                    store_metrics(
                        tenant_id=artist["tenant_id"],
                        artist_id=artist["id"],
                        source="spotify",
                        metrics=result,
                    )
                    emit_event(
                        "scraping:completed",
                        artist_id=artist["id"],
                        metrics=result,
                    )
                else:
                    emit_event(
                        "scraping:failed",
                        artist_id=artist["id"],
                        error=f"Failed after {RETRY_ATTEMPTS} attempts",
                    )

            await browser.close()

    asyncio.run(_run())


def _parse_number(text: str) -> int:
    """Parse formatted number string to int."""
    try:
        return int(text.replace(",", "").replace(".", ""))
    except (ValueError, AttributeError):
        return 0


if __name__ == "__main__":
    run()
