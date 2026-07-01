Feature: Live Data Pipeline — Collectors → Revenue Events
  As a founder of Sonora Digital Corp
  I want artist data to sync automatically from public sources
  So that revenue events are generated without API keys or manual work

  Background:
    Given ABE Music has 3 artists in data/abe-music.json
    And crw is running on port 3000
    And Docker is available on the VPS

  Scenario: Happy path — Deezer collector syncs artist metrics
    Given the sync cycle starts
    When deezer collector fetches data for "Hector Rubio"
    Then the response includes followers, monthly_listeners, top_tracks, popularity, genres
    And the data matches the schema defined in 020-data-policy.md
    And data/abe-music.json is updated with new metrics
    And a backup is saved to state/backups/abe-music/

  Scenario: Sync triggers revenue event for high-value artist
    Given Hector Rubio has 115M+ streams
    When data_sync_completed event is emitted
    Then sales_pipeline generates a qualified lead
    And enterprise_score increases by at least 5 points

  Scenario: Fallback — Deezer fails, Python collector succeeds
    Given crw is unavailable (container down)
    When deezer.py (Python fallback) runs instead
    Then artist data is still fetched successfully
    And a warning is logged: "crw unavailable, using Python fallback"

  Scenario: Edge case — artist not found on Deezer
    Given a new artist "Test Artist" is added to abe-music.json
    When the collector tries to fetch data for "Test Artist"
    Then a warning is logged: "Artist not found on Deezer"
    And existing data for that artist remains unchanged
    And no data loss occurs

  Scenario: Recovery — sync fails 3 times
    Given Deezer API is unreachable
    When the sync fails for the 3rd consecutive time
    Then an alert is triggered
    And the last successful backup is preserved
    And no data corruption occurs

  Scenario: New artist auto-detected
    Given a new artist is added to data/abe-music.json
    When the next sync cycle runs
    Then the collector automatically fetches data for the new artist
    And the artist's metrics are populated
