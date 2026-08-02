Feature: Outbound Campaign
  As a client company
  I want to run an outbound campaign
  So that I can contact potential leads automatically

  Background:
    Given Playwright is installed
    And the scraper module is configured

  Scenario: Search leads for barber niche
    When I run a campaign for "barberias" in "Hermosillo"
    Then the system returns at least 1 lead
    And each lead has name, address, and niche

  Scenario: Campaign creates tenants
    Given the scraper found 3 leads
    When the campaign orchestrator processes them
    Then 3 new tenants are created with lead_type "cold"
    And each tenant has source "campaign_barberias"

  Scenario: Mock mode returns sample data
    Given Playwright is not installed
    When I run a campaign for "barberias"
    Then the system returns 5 mock leads
