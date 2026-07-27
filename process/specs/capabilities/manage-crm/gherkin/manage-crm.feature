Feature: Manage CRM
  As a sales agent
  I want to manage artist CRM contacts and deals
  So that I can track relationships and opportunities

  @P1
  Scenario: Create new contact
    Given an artist profile in the system
    When I create a CRM contact for the artist
    Then the contact is stored with status "lead"
    And the contact is linked to the artist profile

  @P1
  Scenario: Track deal pipeline
    Given a CRM contact exists
    When I create a new deal worth $5000
    Then the deal appears in the pipeline
    And the deal status is "negotiation"
