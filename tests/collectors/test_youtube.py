"""Mock tests for YouTube collector."""
from unittest.mock import patch, MagicMock
from scrapers.collectors.youtube import search_artist


@patch("scrapers.collectors.youtube.subprocess.run")
def test_search_found(mock_run):
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout='{"id": "test123", "title": "Hector Rubio", "view_count": 743000}\n',
    )
    r = search_artist("Hector Rubio")
    assert len(r) > 0
    assert r[0]["title"] == "Hector Rubio"


@patch("scrapers.collectors.youtube.subprocess.run")
def test_search_no_results(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    r = search_artist("Nobody")
    assert r == []


@patch("scrapers.collectors.youtube.subprocess.run")
def test_search_timeout(mock_run):
    import subprocess
    mock_run.side_effect = subprocess.TimeoutExpired(cmd="yt-dlp", timeout=30)
    r = search_artist("Hector Rubio")
    assert r == []  # returns empty list on error


@patch("scrapers.collectors.youtube.subprocess.run")
def test_search_not_found(mock_run):
    mock_run.side_effect = FileNotFoundError()
    r = search_artist("Hector Rubio")
    assert r == []  # returns empty list on error
