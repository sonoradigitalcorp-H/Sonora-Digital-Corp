Feature: Puerta anti-gasto del pipeline libre
  Como operador del sistema
  Quiero que ninguna API de pago se ejecute sin autorización
  Para evitar fugas de gasto como el cargo de $6 con Veo 3

  Scenario: Bloquea proveedor fuera de lista blanca en modo libre
    Given el sistema en modo FREE_TIER_ONLY=true
    When se intenta llamar al proveedor "veo3"
    Then cost_gate rechaza la llamada con error "PROVEEDOR_FUERA_DE_LISTA_BLANCA"
    And no se realiza ninguna peticion de red

  Scenario: Permite proveedor de lista blanca
    Given el sistema en modo FREE_TIER_ONLY=true
    When se intenta llamar al proveedor "hf-zerogpu"
    Then cost_gate aprueba la llamada

  Scenario: Modo pagado requiere presupuesto aprobado
    Given el sistema en modo ALLOW_PAID=true con APPROVED_BUDGET=0.50
    When se intenta llamar al proveedor "fal" con costo estimado 0.30
    Then cost_gate aprueba y registra el gasto en log
