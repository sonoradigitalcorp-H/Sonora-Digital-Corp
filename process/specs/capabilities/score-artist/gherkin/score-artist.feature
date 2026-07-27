Feature: Score Artist
  As a music analyst
  I want to compute artist scores
  So that I can assess performance and readiness

  @P1
  Scenario: Compute artist momentum score
    Given an artist with 6 months of metrics
    When I request a momentum score
    Then the score is computed from weighted metrics
    And the score is normalized between 0 and 100
