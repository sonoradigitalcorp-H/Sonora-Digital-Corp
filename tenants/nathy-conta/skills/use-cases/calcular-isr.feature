Feature: Calcular ISR RESICO
  La contadora puede calcular ISR para clientes en régimen RESICO

  Scenario: Cálculo ISR RESICO tramo 1
    Given el cliente tuvo ingresos de $20,000 MXN en el bimestre
    When se calcula ISR
    Then la tasa es 1.00%
    And el ISR es $200 MXN

  Scenario: Cálculo ISR RESICO tramo 4
    Given el cliente tuvo ingresos de $150,000 MXN en el bimestre
    When se calcula ISR
    Then la tasa es 2.00%
    And el ISR es $3,000 MXN

  Scenario: Cliente excede tope RESICO
    Given el cliente ha facturado $3,600,000 MXN en el año
    When se verifica el tope
    Then el sistema alerta: "EXCEDISTE el tope de $3.5M"
    And recomienda migrar a Actividades Empresariales
