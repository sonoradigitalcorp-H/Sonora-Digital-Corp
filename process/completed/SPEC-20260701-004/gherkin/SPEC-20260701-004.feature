Feature: Capability Registry + Decision Engine
  As a founder of Sonora Digital Corp
  I want the system to automatically select the best provider for each capability
  So that scraping works without hardcoded provider order and handles failures gracefully

  Background:
    Given config/registry.json exists with valid capabilities
    And config/providers.json exists with provider configs

  # --- Registry ---
  Scenario: Load registry successfully
    When the registry is loaded
    Then it contains at least 3 capabilities
    And each capability has at least 1 provider

  Scenario: Query registry by capability ID
    Given capability "acquire-metadata" exists with 4 providers
    When get_capability("acquire-metadata") is called
    Then it returns a Capability with providers ordered by weight

  Scenario: Query non-existent capability returns None
    Given capability "nonexistent" does not exist
    When get_capability("nonexistent") is called
    Then it returns None

  Scenario: List providers ordered by weight ascending
    Given capability "acquire-metadata" has providers [deezer(w=1), apple(w=2), youtube(w=3)]
    When list_providers("acquire-metadata") is called
    Then deezer is first, apple is second, youtube is third

  Scenario: Disabled provider excluded from list
    Given provider "facebook-browser" has enabled=false
    When list_providers("browse-artist") is called
    Then "facebook-browser" is not in the list

  # --- Health ---
  Scenario: Provider health check returns healthy
    Given deezer-api has health_url that returns 200
    When check_provider_health("deezer-api") is called
    Then status is "healthy"

  Scenario: Provider health check returns down
    Given deezer-api has health_url that returns 503
    When check_provider_health("deezer-api") is called
    Then status is "down"

  Scenario: Provider health check times out
    Given health_url does not respond within 5 seconds
    When check_provider_health("deezer-api") is called
    Then status is "degraded"

  Scenario: Provider without health URL assumed healthy
    Given provider has no health_url
    When check_provider_health is called
    Then status is "healthy"

  Scenario: Health cache returns cached value before TTL
    Given health was checked 1 minute ago
    When get_provider_health("deezer-api") is called
    Then it returns cached result without HTTP call

  Scenario: Health cache refreshes after TTL
    Given health was checked 6 minutes ago
    When get_provider_health("deezer-api") is called
    Then it makes a new HTTP call

  # --- Decision Engine ---
  Scenario: Select primary provider when healthy
    Given acquire-metadata has providers [deezer(weight=1, healthy), apple(weight=2, healthy)]
    When select_provider("acquire-metadata") is called
    Then it returns "deezer-api"

  Scenario: Fallback to secondary when primary is down
    Given acquire-metadata has providers [deezer(weight=1, down), apple(weight=2, healthy)]
    When select_provider("acquire-metadata") is called
    Then it returns "apple-music-api"

  Scenario: All providers down raises error
    Given acquire-metadata has providers [deezer(down), apple(down)]
    When select_provider("acquire-metadata") is called
    Then NoProviderAvailableError is raised

  Scenario: Preferred provider is selected when healthy
    Given acquire-metadata has providers [deezer(healthy), apple(healthy)]
    When select_provider("acquire-metadata", preferred_provider="apple-music-api")
    Then it returns "apple-music-api"

  Scenario: Preferred provider down falls back
    Given acquire-metadata has providers [deezer(healthy), apple(down)]
    When select_provider("acquire-metadata", preferred_provider="apple-music-api")
    Then it returns "deezer-api"

  Scenario: Cost filter excludes expensive provider
    Given acquire-metadata has providers [deezer(cost=0, healthy), apple(cost=0.01, healthy)]
    When select_provider("acquire-metadata", max_cost=0.001)
    Then it returns "deezer-api"

  # --- Execute ---
  Scenario: Execute capability returns result with data
    Given deezer-api is healthy and returns valid data
    When execute_capability("acquire-metadata", {"artist_name": "Hector Rubio"})
    Then result.success is True
    And result.data contains "followers"
    And event "CapabilityExecuted" is emitted

  Scenario: Execute with automatic fallback on provider failure
    Given deezer-api returns 503, apple-music-api returns 200
    When execute_capability("acquire-metadata", {"artist_name": "Hector Rubio"})
    Then result.success is True
    And result.provider_id is "apple-music-api"
    And event "ProviderFailed" is emitted for deezer-api

  Scenario: Execute with all providers failing
    Given all providers for acquire-metadata return errors
    When execute_capability("acquire-metadata", {"artist_name": "Hector Rubio"})
    Then result.success is False
    And result.error is not empty
    And event "NoProviderAvailable" is emitted

  # --- Validation ---
  Scenario: Registry rejects capability without providers
    Given a capability with empty providers list
    When the registry is validated
    Then validation error is raised

  Scenario: Registry rejects duplicate provider IDs
    Given a capability with two providers with same id
    When the registry is validated
    Then validation error is raised

  Scenario: Registry accepts valid capability
    Given a capability with all required fields
    When the registry is validated
    Then no error is raised

  # --- Sync Integration ---
  Scenario: Sync uses decision engine
    Given sync.py is configured to use decision engine
    When run_sync_cycle() is called
    Then execute_capability is called instead of direct fetch_artist

  Scenario: Sync produces same output schema
    Given sync.py uses decision engine
    When run_sync_cycle() is called
    Then data/abe-music.json has same schema as before

  Scenario: Sync handles engine failure gracefully
    Given all providers are down
    When run_sync_cycle() is called
    Then data/abe-music.json is not modified
    And last backup is preserved
