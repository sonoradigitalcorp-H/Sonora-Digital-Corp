Feature: Conciliar bancos
  La contadora puede conciliar estados de cuenta contra facturas

  Scenario: Conciliación completa
    Given hay 15 movimientos bancarios en el mes
    And 14 facturas emitidas y recibidas
    When se ejecuta conciliación
    Then 14 movimientos coinciden con facturas
    And 1 movimiento sin identificar es reportado
    And el saldo conciliado coincide con el banco

  Scenario: Discrepancia por pago parcial
    Given un cliente pagó $10,000 MXN por una factura de $12,000
    When se concilia
    Then se detecta diferencia de $2,000 MXN
    And se reporta como pago pendiente parcial

  Scenario: Cargo bancario no identificado
    Given hay un cargo de $500 MXN sin factura asociada
    When se concilia
    Then se reporta como "cargo sin identificar"
    And se sugiere investigar con el banco
