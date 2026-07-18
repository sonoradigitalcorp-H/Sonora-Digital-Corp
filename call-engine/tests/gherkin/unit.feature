Feature: Unit Tests — Orchestrator Engine Edge Cases
  As a developer
  I want the engine to handle all edge cases gracefully
  So that calls never crash or hang

  Background:
    Given A mockCall and mockPlayer are available
    And The engine is configured with mock TTS and mock LLM

  Scenario: engine continues when TTS fails
    When The engine runs and TTS returns an error
    Then The engine logs the error
    And The engine does not crash
    And The engine stops cleanly on Stop()

  Scenario: engine continues when LLM fails
    When The engine runs and LLM returns an error
    Then The engine logs the error
    And The engine does not crash

  Scenario: multiple conversation turns without deadlock
    When The engine runs with 5 mock LLM responses
    Then All 5 turns complete without deadlock
    And The mock sink received frames for each turn

  Scenario: sink accumulates frames correctly
    Given A mock sink
    When 100 frames are written
    Then The sink write count equals 100

  Scenario: player fires OnFinish after source EOF
    Given A mock player with a 5-frame source
    When The player starts playing
    Then OnFinish is called

  Scenario: goroutine cleanup on engine stop
    Given A running engine with active player
    When The engine is stopped
    Then The done channel is closed
    And No goroutines leak
