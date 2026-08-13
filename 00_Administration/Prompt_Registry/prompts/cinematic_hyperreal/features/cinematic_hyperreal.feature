# Feature: Generar imagen cinematográfica de marca SDC
# BDD / TDD — estos steps son los TESTS que el prompt debe cumplir.

  Scenario: Imagen editorial de agente IA para restaurante
    Given una solicitud de imagen "agente IA de WhatsApp para restaurante de Sonora"
    When el prompt se construye con la plantilla cinematic_hyperreal
    Then incluye directiva de luz dorada o rim light
    And incluye profundidad de campo reducida y encuadre editorial
    And incluye contexto de fondo de restaurante desenfocado
    And NO pide texto legible dentro de la imagen
    And estima costo por operación menor o igual a 0.50 dólares
    And especifica resolución 1080x1920 o 1080x1080

  Scenario: Imagen de moda con estética de marca
    Given una solicitud de imagen "ropa de boutique con estética premium"
    When el prompt se construye con la plantilla cinematic_hyperreal
    Then incluye color grading cálido con acento azul/dorado
    And incluye textura realista sin aspecto plastificado
    And respeta tope de 1 imagen por operación

  Scenario: Video corto de demo de producto
    Given una solicitud de video "demo de agente IA respondiendo en WhatsApp"
    When el prompt se construye con la plantilla cinematic_hyperreal
    Then especifica num_frames menor o igual a 64
    And estima costo por operación menor o igual a 0.50 dólares
    And incluye directiva de movimiento mínimo y estable

  Scenario: El prompt NO cumple la spec
    Given un prompt candidato que omite las directivas de luz y composición
    When el spec judge lo evalúa
    Then el veredicto es FAIL y el score es menor a 80
