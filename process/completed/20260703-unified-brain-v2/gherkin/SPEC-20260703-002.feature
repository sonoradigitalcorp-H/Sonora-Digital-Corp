Feature: Unified Brain v2
  As any agent (Hermes, OpenClaw, JARVIS, Telegram bot)
  I want to query the unified brain with natural language
  So that I get answers from the best available source without knowing the store

  Background:
    Given BrainService is running on VPS sdc-prod
    And Neo4j has 366+ Knowledge nodes

  Scenario: Semantic search finds correct node
    Given I query "Neo4j port"
    When unified_brain_query executes in mode auto
    Then I get result with label "Neo4j Bolt" and summary containing "7687"
    And source is "truth"

  Scenario: Type filter returns only matching type
    Given I query "Neo4j" with type_filter="service"
    When unified_brain_query executes
    Then all results have type == "service"
    And total results >= 2 (HTTP + Bolt)

  Scenario: Fallback chain works when Neo4j fails
    Given Neo4j is unreachable
    When unified_brain_query executes
    Then it falls back to Qdrant search
    And returns results with lower score but correct info

  Scenario: Full sync produces no duplicates
    Given BrainSyncer.full_sync() has run once
    When BrainSyncer.full_sync() runs again
    Then no duplicate nodes are created
    And node count remains stable

  Scenario: MCP tool responds via Hermes
    Given MCP brain server is registered in Hermes config.yaml
    When Hermes calls unified_brain_query("load average")
    Then response contains "0.15" (VPS load)
