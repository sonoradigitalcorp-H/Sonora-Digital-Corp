Feature: Sync Artist Data
  As a music industry operator
  I want to sync artist data from multiple providers
  So that I have a unified view of artist performance

  Background:
    Given the system has a collector agent running
    And provider API keys are configured

  @P1 @critical
  Scenario: Sync artist from single provider
    Given an artist "Bad Bunny" with Spotify ID "3IPMEK7b9o8ar4qWEqpHbB"
    When a sync is triggered for provider "spotify"
    Then the system fetches artist data from Spotify API
    And stores normalized profile in Neo4j
    And stores monthly metrics in Qdrant
    And the sync status is "completed"

  @P1 @critical
  Scenario: Deduplicate artist across providers
    Given an artist exists in Neo4j from Spotify
    When the same artist is synced from YouTube
    Then the system matches by ISRC and name similarity
    And merges metrics into the existing profile
    And links YouTube provider ID to same node

  @P2
  Scenario: Handle provider rate limit
    Given the Spotify API returns 429 (rate limited)
    When the sync is triggered
    Then the system waits with exponential backoff
    And retries up to 3 times
    And if all retries fail, sets status to "failed"

  @P2
  Scenario: Incremental sync preserves history
    Given an artist was synced 7 days ago
    When an incremental sync is triggered today
    Then historical metrics are preserved
    And only new data is appended
    And version field is incremented
