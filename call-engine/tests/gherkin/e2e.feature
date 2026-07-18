Feature: E2E Tests — Full System
  As a developer
  I want the complete system to work from call to Neo4j
  So that deployments are safe

  Scenario: full call cycle with scoring saved
    Given A paired MeowCaller session
    And A reachable test number
    When converse runs to completion
    Then The call is placed and reaches ringing state
    And On call end, the scoring module runs
    And A lead record is saved to Neo4j with score

  Scenario: prompt regression against baseline
    Given A baseline JSON file with expected eval results
    When eval_prompts.py runs
    Then All test results match the baseline
