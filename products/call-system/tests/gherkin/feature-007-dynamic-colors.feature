Feature: Dynamic Colors
  As a visitor
  I want the page colors to change with the time of day
  So that the experience feels alive

  Scenario Outline: Color palette at different hours
    Given the time is <hour>:00
    When the page refreshes
    Then the primary color is <color>
    And the hermetic phrase contains <keyword>

    Examples:
      | hour | color     | keyword  |
      | 7    | #f97316   | amanecer |
      | 12   | #06b6d4   | poder    |
      | 16   | #a855f7   | creativo |
      | 20   | #AC6D3E   | ocaso    |
      | 2    | #0f0f1a   | noche    |
