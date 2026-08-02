Feature: Objection Handling
  As the AI assistant
  I want to detect and handle objections properly
  So that I can convert more leads

  Scenario Outlines:
    Given I am in a call with a lead
    When the lead says "<objection>"
    Then the system detects the objection category
    And the response acknowledges the concern
    And the objection is logged for analytics

    Examples:
      | objection                    | category    |
      | "No me interesa"             | interes     |
      | "Ya tengo distribuidor"      | satisfecho  |
      | "Es muy caro"                | precio      |
      | "Lo pienso"                  | tiempo      |
      | "No sé si sirva"             | confianza   |
      | "No tengo presupuesto"       | precio      |
      | "Después vemos"              | tiempo      |
      | "Estoy bien así"             | satisfecho  |

  Scenario: Objection cooldown
    Given the user said an objection 5 seconds ago
    When they say the same objection again
    Then the system does NOT re-detect it as a new objection
