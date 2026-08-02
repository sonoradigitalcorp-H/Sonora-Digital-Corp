Feature: Declarar impuestos SAT
  La contadora puede calcular y presentar declaraciones bimestrales y anuales

  Scenario: Declaración bimestral RESICO
    Given el cliente tiene ingresos de $120,000 MXN en el bimestre
    And está en régimen RESICO
    When se calcula ISR del bimestre
    Then la tasa aplicada es 2.00%
    And el ISR a pagar es $2,400 MXN
    And se genera declaración lista para presentar

  Scenario: Recordatorio de tope RESICO
    Given el cliente ha acumulado $3,300,000 MXN en el año
    When el sistema verifica el tope anual
    Then alerta: "Has alcanzado 94% del tope de $3.5M"
    And sugiere planificar migración de régimen

  Scenario: Declaración anual persona física
    Given el cliente tuvo ingresos como honorarios
    And gastos deducibles por $80,000 MXN
    When se calcula declaración anual
    Then se aplican deducciones personales
    And se determina ISR anual definitivo
