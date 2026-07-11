Feature: <Name>
  As a <role>
  I want to <action>
  So that <benefit>

  Background:
    Given <common context>

  @happy
  Scenario: <happy path name>
    Given <precondition>
    When <action>
    Then <expected result>

  @edge
  Scenario: <edge case name>
    Given <precondition>
    When <action>
    Then <expected result>

  @error
  Scenario: <error case name>
    Given <precondition>
    When <action>
    Then <expected error>
