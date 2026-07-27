Feature: Procesar nómina
  La contadora puede generar CFDI de nómina para empleados

  Scenario: Nómina ordinaria quincenal
    Given un empleado con SDI de $500 MXN
    And trabajó 15 días del periodo
    When se genera CFDI de nómina
    Then percepción por sueldo es $7,500 MXN
    And se calcula ISR según tabla
    And se genera XML timbrado

  Scenario: Finiquito por renuncia
    Given un empleado renuncia después de 2 años
    And tiene salario diario de $300 MXN
    When se calcula finiquito
    Then incluye 12 días de vacaciones no tomadas
    And prima vacacional (25%)
    And aguinaldo proporcional (20 días / año)
    And se genera CFDI de nómina por finiquito

  Scenario: Incidencia por incapacidad
    Given un empleado tiene incapacidad de 5 días por IMSS
    When se procesa la incidencia
    Then el periodo de incapacidad se resta del SDI
    And el IMSS cubre el monto correspondiente
    And se refleja en el CFDI de nómina
