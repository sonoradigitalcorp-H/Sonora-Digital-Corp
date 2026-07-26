from pytest_bdd import scenario

from tests.steps.sync_artist_data_steps import *


@scenario("sync-artist-data.feature", "Sync artist from single provider")
def test_sync_single_provider():
    pass


@scenario("sync-artist-data.feature", "Handle provider rate limit")
def test_rate_limit():
    pass


@scenario("sync-artist-data.feature", "Incremental sync preserves history")
def test_incremental_sync():
    pass
