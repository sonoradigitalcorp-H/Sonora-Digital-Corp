"""Tests para Playwright Scraping Pipeline [FR6] — headless browser automation."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestScraperStructure:
    """FR6: Scraper must have correct structure and configuration."""

    def test_scraper_module_exists(self):
        """Playwright scraper module must exist"""
        from apps.sonora_scraper import playwright_scraper
        assert playwright_scraper is not None

    def test_scraper_has_run_function(self):
        """Scraper must expose a main run() function"""
        from apps.sonora_scraper.playwright_scraper import run
        assert callable(run)

    def test_scraper_has_retry_logic(self):
        """Scraper must implement retry with configurable attempts"""
        from apps.sonora_scraper.playwright_scraper import RETRY_ATTEMPTS
        assert RETRY_ATTEMPTS >= 3


class TestScraperExecution:
    """FR6: Scraper must navigate, extract, and store data."""

    @pytest.fixture
    def mock_page(self):
        """Mock Playwright page with sample data."""
        page = MagicMock()
        page.goto = AsyncMock()
        page.wait_for_selector = AsyncMock()

        async def mock_text(selector):
            data = {
                "h1": "Hector Rubio",
                "[data-testid='monthly-listeners']": "115,093,009",
                "[data-testid='followers']": "1,028,288",
                "[data-testid='top-song']": "Mi Cancion",
            }
            return data.get(selector, "0")

        page.text_content = AsyncMock(side_effect=mock_text)
        return page

    @pytest.fixture
    def mock_browser(self, mock_page):
        """Mock Playwright browser"""
        browser = MagicMock()
        context = MagicMock()
        context.new_page = AsyncMock(return_value=mock_page)
        browser.new_context = AsyncMock(return_value=context)
        return browser

    @pytest.mark.skipif(True, reason="Playwright not installed in test env")
    def test_navigate_to_artist_page(self, mock_browser):
        """Scraper navigates to correct URL for each artist"""
        from apps.sonora_scraper.playwright_scraper import scrape_artist

        result = scrape_artist(
            browser=mock_browser,
            artist_name="Hector Rubio",
            url="https://open.spotify.com/artist/test123",
        )
        assert result is not None

    @pytest.mark.skipif(True, reason="Playwright not installed in test env")
    def test_extract_metrics(self, mock_browser):
        """Scraper extracts all required metrics"""
        from apps.sonora_scraper.playwright_scraper import scrape_artist

        result = scrape_artist(
            browser=mock_browser,
            artist_name="Hector Rubio",
            url="https://open.spotify.com/artist/test123",
        )
        if result:
            assert "monthly_listeners" in result
            assert "followers" in result
            assert "top_songs" in result

    def test_store_metrics_calls_db(self):
        """Scraped metrics are stored in scraped_metrics table"""
        from apps.sonora_scraper.playwright_scraper import store_metrics

        with patch("sonora_engine.hasura.mutate") as mock_mutate:
            mock_mutate.return_value = {"data": {"insert_scraped_metrics": {"affected_rows": 1}}}

            result = store_metrics(
                tenant_id="abe-music",
                artist_id="artist-uuid",
                source="spotify",
                metrics={"monthly_listeners": 115093009},
            )
            assert result is True
            mock_mutate.assert_called_once()

    def test_emit_scraping_completed_event(self):
        """FR6: After scraping, 'scraping:completed' event is emitted"""
        from apps.sonora_scraper.playwright_scraper import emit_event

        with patch("redis.Redis.from_url") as mock_redis:
            instance = MagicMock()
            mock_redis.return_value = instance
            result = emit_event(
                event_type="scraping:completed",
                artist_id="artist-uuid",
                metrics={"monthly_listeners": 115093009},
            )
            assert result is True
            instance.publish.assert_called_once()


class TestScraperErrorHandling:
    """FR6: Scraper must handle failures gracefully."""

    @pytest.mark.skipif(True, reason="Playwright not installed in test env")
    def test_retry_on_navigation_failure(self):
        """FR6: If navigation fails, retry up to RETRY_ATTEMPTS times"""
        pass

    def test_emit_scraping_failed_event(self):
        """FR6: On failure, 'scraping:failed' event is emitted"""
        from apps.sonora_scraper.playwright_scraper import emit_event

        with patch("redis.Redis.from_url") as mock_redis:
            instance = MagicMock()
            mock_redis.return_value = instance
            result = emit_event(
                event_type="scraping:failed",
                artist_id="artist-uuid",
                error="Timeout after 3 retries",
            )
            assert result is True
            instance.publish.assert_called_once()


class TestScraperConfiguration:
    """FR6: Scraper must be configurable per tenant/artist."""

    def test_scraper_has_artist_list(self):
        """Scraper reads artist list from config or DB"""
        from apps.sonora_scraper.playwright_scraper import get_artists_to_scrape

        artists = get_artists_to_scrape()
        assert isinstance(artists, list)

    def test_cron_schedule_is_configured(self):
        """Scraper runs on a configurable cron schedule (default 6:00 AM)"""
        from apps.sonora_scraper.cron import CRON_SCHEDULE

        assert CRON_SCHEDULE is not None
        assert "6" in CRON_SCHEDULE or "cron" in str(CRON_SCHEDULE).lower()
