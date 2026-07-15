Feature: Finanzas del artista
  Como artista musical
  Quiero registrar y consultar mis finanzas
  Para tener control de mis ingresos y gastos

  Background:
    Given soy un artista registrado en ABE Music

  Scenario: Registrar ingreso
    When registro un ingreso de $85,000 por "Presentación Foro Sol"
    Then el ingreso queda registrado en mi historial

  Scenario: Registrar gasto
    When registro un gasto de $25,000 por "Producción"
    Then el gasto queda registrado en mi historial

  Scenario: Generar reporte mensual
    When solicito el reporte financiero de "2026-06"
    Then veo ingresos, gastos y utilidad del mes
    And veo el detalle de top ingresos y gastos

  Scenario: Conciliar con Contpaqi
    When solicito conciliación del periodo "2026-06"
    Then veo las transacciones conciliadas
    And veo las discrepancias detectadas
