Feature: Governance as Code
  Scenario: Pre-commit hook blocks commit without spec
    Given there is no active spec
    When I try to commit
    Then the commit is blocked
