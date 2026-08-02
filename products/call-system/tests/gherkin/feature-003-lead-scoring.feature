Feature: Lead Scoring and Classification
  As the system
  I want to classify leads as cold, warm, or hot
  So that I can adjust the conversation accordingly

  Scenario: New campaign lead is cold
    Given a tenant created from a campaign with 0 calls
    When the system checks the lead type
    Then it returns "cold"

  Scenario: Trial user with multiple calls is warm
    Given a tenant with plan "trial" and 3 calls
    When the system checks the lead type
    Then it returns "warm"

  Scenario: Enterprise tenant is hot
    Given a tenant with tier "enterprise"
    When the system checks the lead type
    Then it returns "hot"

  Scenario: Call improves lead score
    Given a cold lead with score 20
    When the call ends with positive sentiment
    Then the lead score increases
