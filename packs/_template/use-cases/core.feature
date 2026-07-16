Feature: {Feature Name}
  As a {role}
  I want {feature}
  So that {benefit}

  Background:
    Given el sistema está operativo
    And el tenant "{tenant_id}" está activo
    And la API key de OpenRouter está configurada

  @flow-principal
  Scenario: {Scenario Name}
    Given {precondition}
    When {action}
    Then {expected_result}

  @flow-secundario
  Scenario: {Alternative Scenario}
    Given {precondition}
    When {action}
    Then {expected_result}
