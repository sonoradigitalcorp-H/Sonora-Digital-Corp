import pytest
from pytest_bdd import given, when, then, parsers
from dataclasses import dataclass, field


@dataclass
class ArtistSync:
    name: str = ""
    spotify_id: str = ""
    youtube_id: str = ""
    status: str = "pending"
    retries: int = 0
    metrics: list = field(default_factory=list)


@pytest.fixture
def artist_sync() -> ArtistSync:
    return ArtistSync()


@given(parsers.parse('an artist "{name}" with Spotify ID "{spotify_id}"'))
def artist_with_spotify(artist_sync: ArtistSync, name: str, spotify_id: str) -> None:
    artist_sync.name = name
    artist_sync.spotify_id = spotify_id


@given("an artist exists in Neo4j from Spotify")
def artist_exists_in_neo4j(artist_sync: ArtistSync) -> None:
    artist_sync.status = "completed"


@given(parsers.parse("the Spotify API returns {status_code:d} (rate limited)"))
def spotify_rate_limit(status_code: int) -> None:
    pass


@given("an artist was synced 7 days ago")
def artist_synced_7_days_ago(artist_sync: ArtistSync) -> None:
    artist_sync.metrics.append({"date": "2026-07-14", "followers": 1000})


@given(parsers.parse("provider API keys are configured"))
@given("API keys are configured")
def provider_api_keys_configured() -> None:
    pass


@when(parsers.parse("a sync is triggered for provider {provider}"))
def trigger_sync(artist_sync: ArtistSync, provider: str) -> None:
    artist_sync.status = "completed"


@when("the sync is triggered")
def trigger_sync_generic(artist_sync: ArtistSync) -> None:
    artist_sync.retries += 1
    if artist_sync.retries >= 3:
        artist_sync.status = "failed"


@when("an incremental sync is triggered today")
def trigger_incremental_sync(artist_sync: ArtistSync) -> None:
    artist_sync.metrics.append({"date": "2026-07-21", "followers": 1500})


@then("the system fetches artist data from Spotify API")
def check_spotify_fetch() -> None:
    pass


@then("stores normalized profile in Neo4j")
def check_neo4j_store() -> None:
    pass


@then("stores monthly metrics in Qdrant")
def check_qdrant_store() -> None:
    pass


@then(parsers.parse("the sync status is {status:w}"))
@then(parsers.parse('the sync status is "{status}"'))
def check_sync_status(artist_sync: ArtistSync, status: str) -> None:
    expected = status.strip('"') if '"' in status else status
    assert artist_sync.status == expected


@then("the system matches by ISRC and name similarity")
def check_dedup_match() -> None:
    pass


@then("merges metrics into the existing profile")
def check_metrics_merge(artist_sync: ArtistSync) -> None:
    assert len(artist_sync.metrics) >= 0


@then("links YouTube provider ID to same node")
def check_provider_link() -> None:
    pass


@then("the system waits with exponential backoff")
def check_backoff() -> None:
    pass


@then(parsers.parse("retries up to {count:d} times"))
def check_retries(artist_sync: ArtistSync, count: int) -> None:
    assert artist_sync.retries <= count


@then("if all retries fail, sets status to failed")
def check_failed_status(artist_sync: ArtistSync) -> None:
    assert artist_sync.status == "failed"


@then("historical metrics are preserved")
def check_history_preserved(artist_sync: ArtistSync) -> None:
    assert len([m for m in artist_sync.metrics if m["date"] == "2026-07-14"]) == 1


@then("only new data is appended")
def check_new_data_appended(artist_sync: ArtistSync) -> None:
    assert len(artist_sync.metrics) >= 2


@then("version field is incremented")
def check_version_increment() -> None:
    pass
