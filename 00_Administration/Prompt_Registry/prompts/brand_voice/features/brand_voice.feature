# Feature: Voz de marca de Sonora Digital Corp (brand_voice)
# BDD / TDD — estos steps son los TESTS que el copy/prompt debe cumplir.

  Scenario: Caption de post respeta la voz de marca
    Given un copy candidato para un post de Instagram
    When se construye con la plantilla brand_voice
    Then tiene menos de 100 palabras
    And usa español mexicano sin anglicismos
    And incluye CTA de comentar una palabra clave
    And NO usa más de 1 emoji
    And NO usa TODO MAYÚSCULAS ni exclamaciones reiteradas

  Scenario: Mensaje DM a lead es cálido y ejecutivo
    Given un mensaje candidato para un lead
    When se construye con la plantilla brand_voice
    Then reconoce el negocio del lead
    And ofrece demo gratis con CTA claro
    And NO usa lenguaje de vendedor agresivo

  Scenario: Colores de marca son respetados
    Given una pieza visual candidata
    When usa los colores de la paleta de marca
    Then el azul profundo #0A2540 es el color base
    And el dorado #C9A227 se usa en acentos (10-15%)
    And NO usa neón
