Feature: JARVIS Proactive Engine

  Background:
    Given JARVIS is running with continuous mic
    And WebSocket is connected on port 8769

  Scenario: Wake word activation
    When user says "Hey JARVIS"
    Then JARVIS should activate
    And voice status should show "listening"

  Scenario: Shutdown command
    Given JARVIS is listening
    When user says "apaga micrófono"
    Then JARVIS should stop listening
    And voice status should show "muted"

  Scenario: Action execution with confirmation
    When user says "publica esto en twitter"
    Then JARVIS should ask for confirmation
    And JARVIS should NOT execute until confirmed
