Feature: Prompt Evals — Call Agent Prompts
  As a developer
  I want the LLM prompts to produce high-quality responses
  So that the call agent sounds natural and converts leads

  Scenario: call_agent identifies SDC in first greeting
    Given A warm lead named Nathaly
    When The call agent prompt is evaluated
    Then The response contains "Sonora Digital Corp"
    And The response does NOT contain "pagar ahora"

  Scenario: objection_handler validates before responding
    Given A lead says "No tengo tiempo"
    When The objection handler prompt is evaluated
    Then The response acknowledges the objection first
    And The response does NOT contain "insisto" or "obligado"

  Scenario: lead_scoring returns valid JSON for hot lead
    Given A transcript where lead says "¿Cuándo empezamos?"
    When The scoring prompt is evaluated
    Then The response is valid JSON with score "hot"

  Scenario: followup prompt generates actionable message
    Given A lead scored "warm" with interest in agents
    When The followup prompt is evaluated
    Then The response includes a next step with SDC branding

  Scenario: summary prompt extracts key points
    Given A full call transcript with objections and outcomes
    When The summary prompt is evaluated
    Then The response includes outcome, objections, and next_step

  Scenario: multi-turn maintains context
    Given A conversation with 3 exchanges
    When The call_agent prompt is evaluated at each turn
    Then Each response references the previous exchange

  Scenario: responses are always in Spanish
    Given Any lead input in Spanish
    When The call_agent prompt is evaluated
    Then The response is in Spanish
