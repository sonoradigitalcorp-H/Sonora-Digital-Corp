Feature: Campañas de promoción
  Como artista musical
  Quiero crear y medir campañas publicitarias
  Para promocionar mi música efectivamente

  Background:
    Given soy un artista registrado en ABE Music

  Scenario: Crear campaña en Meta Ads
    When creo una campaña llamada "Lanzamiento Junio" con presupuesto de $5,000
    Then la campaña queda activa
    And recibo confirmación con los detalles

  Scenario: Pausar campaña activa
    Given tengo una campaña activa "Lanzamiento Junio"
    When pauso la campaña
    Then su estado cambia a "pausada"

  Scenario: Medir ROI de campaña
    When consulto el ROI de mis campañas
    Then veo inversión, alcance y retorno
    And veo el costo por conversión
