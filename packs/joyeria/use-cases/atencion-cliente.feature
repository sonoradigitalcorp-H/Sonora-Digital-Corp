Feature: Atención al cliente de joyería
  As a cliente
  I want resolver dudas y problemas con mi compra
  So that tenga una experiencia satisfactoria

  Background:
    Given el sistema está operativo
    And el tenant "joyeria_{cliente}" está activo

  @flow-garantia
  Scenario: Cliente usa garantía
    Given un cliente tiene una joya con defecto de fabricación
    When el cliente contacta dentro del año de garantía
    Then el sistema genera una orden de reparación sin costo
    And programa recogida del producto

  @flow-seguimiento
  Scenario: Cliente rastrea su pedido
    Given un cliente realizó una compra hace 3 días
    When el cliente pregunta por el estado de su pedido
    Then el sistema consulta el estatus en Shopify
    And responde con número de guía y fecha estimada de entrega

  @flow-info-producto
  Scenario: Cliente pregunta cuidados de una joya
    Given un cliente compró una pieza con piedras preciosas
    When el cliente pregunta cómo cuidarla
    Then el sistema recomienda: evitar químicos, guardar por separado, limpiar con paño suave
