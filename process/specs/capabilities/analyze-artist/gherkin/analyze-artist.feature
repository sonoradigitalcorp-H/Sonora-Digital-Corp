Feature: Analyze Artist
  As a music executive
  I want to analyze artist performance
  So that I can identify trends and opportunities

  @P1
  Scenario: Trend analysis
    Given an artist with historical data
    When I request a trend analysis
    Then the analysis covers at least 6 months
    And trends are compared against peer artists
