Feature: A/B Testing
  As the system operator
  I want to test different prompt variants
  So that I can improve call conversion rates

  Scenario: Tenant is assigned a variant
    Given a new tenant calls for the first time
    When the system assigns an A/B variant
    Then the variant is one of A, B, or C

  Scenario: Variant distribution follows weights
    Given 100 tenants are created
    When each is assigned a variant
    Then approximately 34% get A, 33% get B, 33% get C

  Scenario: Best variant is promoted
    Given variant A has avg score 85 over 30 calls
    And variant B has avg score 60 over 30 calls
    When the evolution hook runs
    Then it proposes switching all traffic to variant A

  Scenario: Auto-optimize applies winner
    Given min_samples is 10
    And variant A has score 80
    And variant B has score 60
    When auto_optimize is true
    Then the system shifts 100% traffic to variant A
