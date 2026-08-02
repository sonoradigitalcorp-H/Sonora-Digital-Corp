Feature: Booking de presentaciones
  Como artista musical
  Quiero gestionar mi agenda de presentaciones
  Para organizar mis fechas y cotizaciones

  Background:
    Given soy un artista registrado en ABE Music

  Scenario: Consultar disponibilidad
    When consulto mi disponibilidad
    Then veo las fechas disponibles para contratar
    And veo las fechas ya reservadas

  Scenario: Cotizar presentación
    When un contratante solicita cotización para "2026-09-05" en "Guadalajara"
    Then genero una cotización con fee sugerido
    And incluyo los términos del evento

  Scenario: Confirmar evento
    Given tengo una cotización aceptada
    When confirmo el evento
    Then el estado cambia a "confirmado"
    And se genera el contrato

  Scenario: Cancelar evento
    Given tengo un evento confirmado
    When cancelo el evento
    Then el estado cambia a "cancelado"
