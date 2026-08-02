Feature: Autonomous Daemon
  As the system operator
  I want the daemon to run campaigns and outreach automatically
  So that leads are generated without manual intervention

  Scenario: Campaign runs every 6 hours
    Given the daemon has been running for 6 hours
    When the campaign interval triggers
    Then Playwright searches for leads in 4 niches
    And new tenants are created with lead_type "cold"

  Scenario: Outreach contacts pending leads
    Given there are pending leads
    When the outreach interval triggers
    Then the system generates a WhatsApp message
    And marks the lead as "contacted"

  Scenario: Evolution runs every 24 hours
    Given the daemon has been running for 24 hours
    When the evolution interval triggers
    Then it evaluates patterns in calls and scores
    And applies improvements if score > 60

  Scenario: Daemon logs state
    Given the daemon is running
    When any action completes
    Then state is saved to daemon_state.json
